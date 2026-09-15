import os
from datetime import datetime, timedelta, timezone
from typing import Any

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

TOKEN_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
STATS_URL = "https://sh.dataspace.copernicus.eu/statistics/v1"

CLIENT_ID = os.getenv("COPERNICUS_CLIENT_ID")
CLIENT_SECRET = os.getenv("COPERNICUS_CLIENT_SECRET")

# En producción se puede restringir a la URL de GitHub Pages.
# Para el mini proyecto dejamos "*" para facilitar las primeras pruebas.
ALLOWED_ORIGINS = [x.strip() for x in os.getenv("ALLOWED_ORIGINS", "*").split(",") if x.strip()]

app = FastAPI(
    title="PastureRestore API",
    version="2.0.0",
    description="API mínima para obtener NDVI real de Sentinel-2 para un polígono."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS != ["*"] else ["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GeometryRequest(BaseModel):
    geometry: dict[str, Any]
    days: int = Field(default=30, ge=1, le=90)
    max_cloud_coverage: int = Field(default=30, ge=0, le=100)


@app.get("/")
def root():
    return {
        "project": "PastureRestore",
        "api": "2.0.0",
        "status": "online",
        "service": "Sentinel-2 NDVI"
    }


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "copernicus_configured": bool(CLIENT_ID and CLIENT_SECRET)
    }


def get_access_token() -> str:
    if not CLIENT_ID or not CLIENT_SECRET:
        raise HTTPException(
            status_code=503,
            detail="Faltan COPERNICUS_CLIENT_ID y COPERNICUS_CLIENT_SECRET en las variables de entorno."
        )

    response = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
        timeout=30,
    )

    if not response.ok:
        raise HTTPException(
            status_code=502,
            detail=f"Error autenticando con Copernicus: HTTP {response.status_code}"
        )

    return response.json()["access_token"]


def build_stats_request(
    geometry: dict[str, Any],
    start_date: str,
    end_date: str,
    max_cloud_coverage: int
) -> dict[str, Any]:
    # NDVI = (B08 - B04) / (B08 + B04)
    # dataMask elimina píxeles sin datos.
    evalscript = """
//VERSION=3
function setup() {
  return {
    input: [{
      bands: ["B04", "B08", "dataMask"]
    }],
    output: [
      {
        id: "ndvi",
        bands: 1,
        sampleType: "FLOAT32"
      },
      {
        id: "dataMask",
        bands: 1
      }
    ]
  };
}

function evaluatePixel(samples) {
  let denominator = samples.B08 + samples.B04;
  let ndvi = denominator === 0 ? -1 : (samples.B08 - samples.B04) / denominator;

  return {
    ndvi: [ndvi],
    dataMask: [samples.dataMask]
  };
}
"""

    return {
        "input": {
            "bounds": {
                "geometry": geometry,
                "properties": {
                    "crs": "http://www.opengis.net/def/crs/EPSG/0/4326"
                }
            },
            "data": [{
                "type": "sentinel-2-l2a",
                "dataFilter": {
                    "maxCloudCoverage": max_cloud_coverage,
                    "mosaickingOrder": "leastCC"
                }
            }]
        },
        "aggregation": {
            "timeRange": {
                "from": f"{start_date}T00:00:00Z",
                "to": f"{end_date}T23:59:59Z"
            },
            "aggregationInterval": {
                "of": "P1D"
            },
            "evalscript": evalscript,
            "resx": 10,
            "resy": 10
        }
    }


def extract_latest_valid_result(payload: dict[str, Any]) -> dict[str, Any]:
    rows = payload.get("data", [])

    # El API devuelve intervalos diarios. Recorremos desde el más reciente.
    for row in reversed(rows):
        outputs = row.get("outputs", {})
        ndvi_output = outputs.get("ndvi", {})
        bands = ndvi_output.get("bands", {})
        band0 = bands.get("B0", {})
        stats = band0.get("stats")

        if stats and stats.get("sampleCount", 0) > 0:
            mean = stats.get("mean")
            if mean is not None:
                interval = row.get("interval", {})
                date_value = interval.get("from", "")[:10]

                return {
                    "ndvi": round(float(mean), 4),
                    "date": date_value,
                    "sample_count": stats.get("sampleCount", 0),
                    "min": stats.get("min"),
                    "max": stats.get("max"),
                    "stdev": stats.get("stDev"),
                    "source": "Sentinel-2 L2A / Copernicus Data Space"
                }

    raise HTTPException(
        status_code=404,
        detail="No se encontraron píxeles válidos de Sentinel-2 en el período solicitado."
    )


@app.post("/api/ndvi")
def ndvi(request: GeometryRequest):
    if request.geometry.get("type") != "Polygon":
        raise HTTPException(
            status_code=400,
            detail="La geometría debe ser un GeoJSON Polygon."
        )

    coordinates = request.geometry.get("coordinates")
    if not coordinates or not coordinates[0] or len(coordinates[0]) < 4:
        raise HTTPException(
            status_code=400,
            detail="El polígono no tiene suficientes vértices."
        )

    now = datetime.now(timezone.utc).date()
    start = now - timedelta(days=request.days)

    token = get_access_token()

    body = build_stats_request(
        request.geometry,
        start.isoformat(),
        now.isoformat(),
        request.max_cloud_coverage
    )

    response = requests.post(
        STATS_URL,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        json=body,
        timeout=90,
    )

    if not response.ok:
        detail = response.text[:1000]
        raise HTTPException(
            status_code=502,
            detail=f"Error de Sentinel Hub Statistical API: HTTP {response.status_code}. {detail}"
        )

    return extract_latest_valid_result(response.json())
