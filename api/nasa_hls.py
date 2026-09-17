import os
import tempfile
from datetime import datetime, timedelta, timezone
from typing import Any

# ============================================================
# Configuración crítica para evitar que GDAL se cuelgue con URLs remotas de la NASA
# ============================================================
os.environ['GDAL_DISABLE_READDIR_ON_OPEN'] = 'YES_DEEP'
os.environ['CPL_VSIL_CURL_ALLOWED_EXTENSIONS'] = '.tif,.TIF'
os.environ['GDAL_HTTP_UNSAFESTSL'] = 'YES'
os.environ['VSI_CACHE'] = 'TRUE'
os.environ['VSI_CACHE_SIZE'] = '50000000'  # 50 MB de caché

import numpy as np
import rasterio
from rasterio.mask import mask
from rasterio.warp import transform_geom
import requests
from fastapi import HTTPException

CMR_URL = "https://cmr.earthdata.nasa.gov/search/granules.json"


def obtener_token_nasa() -> str:
    token = os.getenv("NASA_EARTHDATA_TOKEN", "").strip()
    if not token or "pegar_aqui" in token:
        raise HTTPException(
            status_code=503,
            detail="Falta NASA_EARTHDATA_TOKEN en las variables de entorno."
        )
    return token


def extraer_bbox(geometry: dict[str, Any]) -> str:
    """Extrae el bounding box min_lon,min_lat,max_lon,max_lat del GeoJSON."""
    coords = geometry.get("coordinates", [])
    if not coords or not coords[0]:
        raise HTTPException(status_code=400, detail="Geometría inválida.")
    
    # Maneja polígonos simples y multipolígonos
    anillo = coords[0] if geometry.get("type") == "Polygon" else coords[0][0]
    lons = [p[0] for p in anillo]
    lats = [p[1] for p in anillo]
    
    min_lon, max_lon = min(lons), max(lons)
    min_lat, max_lat = min(lats), max(lats)
    return f"{min_lon},{min_lat},{max_lon},{max_lat}"


def buscar_granulos_cmr(bbox: str, days: int = 30) -> list[dict[str, Any]]:
    """Busca gránulos de vegetación HLS (Sentinel-2 y Landsat) en NASA CMR."""
    now = datetime.now(timezone.utc).date()
    start = now - timedelta(days=days)
    temporal = f"{start.isoformat()}T00:00:00Z,{now.isoformat()}T23:59:59Z"

    # Buscamos primero en HLSS30_VI (Sentinel-2) y como alternativa HLSL30_VI (Landsat)
    params = {
        "short_name": ["HLSS30_VI", "HLSL30_VI"],
        "version": "2.0",
        "bounding_box": bbox,
        "temporal": temporal,
        "sort_key": "-start_date",
        "page_size": 6
    }

    try:
        response = requests.get(CMR_URL, params=params, timeout=15)
        if not response.ok:
            return []
        data = response.json()
        return data.get("feed", {}).get("entry", [])
    except Exception:
        return []


def procesar_ndvi_nasa(geometry: dict[str, Any], days: int = 30, max_cloud_coverage: int = 30) -> dict[str, Any]:
    """Descarga el gránulo NDVI más reciente de la NASA y calcula estadísticas zonales."""
    token = obtener_token_nasa()
    bbox = extraer_bbox(geometry)
    granulos = buscar_granulos_cmr(bbox, days)

    if not granulos:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron imágenes satelitales recientes en NASA HLS para esta zona."
        )

    for granulo in granulos:
        # Encontrar link de la banda NDVI
        ndvi_url = None
        for link in granulo.get("links", []):
            href = link.get("href", "")
            if href.endswith(".NDVI.tif") and href.startswith("https://"):
                ndvi_url = href
                break

        if not ndvi_url:
            continue

        fecha_str = granulo.get("time_start", "")[:10]

        # Descarga en streaming hacia archivo temporal
        try:
            headers = {"Authorization": f"Bearer {token}"}
            with requests.get(ndvi_url, headers=headers, stream=True, timeout=25) as r:
                if not r.ok:
                    continue

                with tempfile.NamedTemporaryFile(suffix=".tif", delete=False) as tmp_file:
                    tmp_path = tmp_file.name
                    for chunk in r.iter_content(chunk_size=65536):
                        if chunk:
                            tmp_file.write(chunk)

            # Procesamiento geoespacial con rasterio
            try:
                with rasterio.open(tmp_path) as ds:
                    geom_proj = transform_geom("EPSG:4326", ds.crs, geometry)
                    try:
                        out_image, _ = mask(ds, [geom_proj], crop=True, nodata=-9999)
                    except ValueError:
                        # Polígono fuera de la extensión de este gránulo específico
                        continue

                    band_data = out_image[0]
                    valid_pixels = band_data[band_data != -9999]
                    valid_pixels = valid_pixels[~np.isnan(valid_pixels)]

                    # Filtrar posibles valores atípicos fuera de rango NDVI válido (-2000 a 10000)
                    valid_pixels = valid_pixels[(valid_pixels >= -2000) & (valid_pixels <= 10000)]

                    if len(valid_pixels) == 0:
                        continue

                    # Factor de escala oficial de NASA HLS: 0.0001
                    ndvi_real = valid_pixels * 0.0001
                    mean_val = float(np.mean(ndvi_real))
                    min_val = float(np.min(ndvi_real))
                    max_val = float(np.max(ndvi_real))
                    std_val = float(np.std(ndvi_real))

                    return {
                        "ndvi": round(mean_val, 4),
                        "date": fecha_str,
                        "sample_count": int(len(valid_pixels)),
                        "min": round(min_val, 4),
                        "max": round(max_val, 4),
                        "stdev": round(std_val, 4),
                        "source": "NASA HLS (Harmonized Landsat Sentinel-2)"
                    }
            finally:
                if os.path.exists(tmp_path):
                    try:
                        os.remove(tmp_path)
                    except OSError:
                        pass
        except Exception:
            continue

    raise HTTPException(
        status_code=404,
        detail="No se encontraron píxeles válidos en las imágenes de NASA HLS para este polígono."
    )
