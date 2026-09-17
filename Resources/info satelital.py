import os
import zipfile
import json
import urllib.request

# Let's inspect the page content or create a structured developer/integration guide package for "Antigravity"
# to connect their app to NASA's Harmonized Landsat Sentinel-2 (HLS) data service via Earthdata / LP DAAC APIs / CMR (Common Metadata Repository).

os.makedirs('/tmp/nasa_hls_package', exist_ok=True)

# 1. Create a README / Integration guide for Antigravity
readme_content = """# NASA HLS (Harmonized Landsat Sentinel-2) Integration Guide for Antigravity

This package contains technical documentation, API endpoints, Python client code examples, and integration architecture for connecting your application to NASA's HLS satellite data streams (specifically Sentinel-2 Multi-spectral Instrument Vegetation Indices Daily Global 30m V2.0 - HLSS30_VI).

## Dataset Overview
- **Shortname:** HLSS30_VI (Version 2.0)
- **Satellites:** Sentinel-2A, Sentinel-2B, and Sentinel-2C (ESA / Copernicus) combined with Landsat 8/9 via NASA HLS project.
- **Resolution:** 30 meters, MGRS tiling system.
- **Format:** Cloud Optimized GeoTIFF (COG), separate files per band/index (NDVI, EVI, SAVI, MSAVI, NDMI, NDWI, NBR, NBR2, TVI).
- **Access Protocol:** NASA Earthdata Login (OAuth2), NASA CMR (Common Metadata Repository), and LP DAAC Direct Access via AWS S3 (us-west-2).

---

## Architecture & Connection Strategy

To connect your app to NASA's satellite data:
1. **Authentication:** Register an account at [NASA Earthdata Login](https://urs.earthdata.nasa.gov/). Configure `.netrc` or environment tokens for programmatic access.
2. **Discovery (CMR API):** Query NASA's Common Metadata Repository to find spatial/temporal granules matching user coordinates.
3. **Data Retrieval (Direct S3 or HTTPS):** Stream Cloud Optimized GeoTIFFs (COGs) directly from NASA LP DAAC cloud storage in AWS S3 (`s3://lp-prod-protected/HLSS30_VI.002/...`) or via HTTPS HTTPS/OPeNDAP.

---

## Included Files
- `client_example.py`: Ready-to-use Python script to query CMR and fetch vegetation indices for any bounding box/lat-lon.
- `api_endpoints.json`: Official service URLs, CMR endpoints, and Earthdata login configurations.
- `metadata_summary.json`: Detailed specification of the HLSS30_VI bands and vegetation indices.
"""

with open('/tmp/nasa_hls_package/README.md', 'w') as f:
    f.write(readme_content)

# 2. Create api_endpoints.json
endpoints = {
    "dataset_title": "HLS Sentinel-2 Multi-spectral Instrument Vegetation Indices Daily Global 30 m V2.0",
    "doi": "10.5067/HLS/HLSS30_VI.002",
    "cmr_search_endpoint": "https://cmr.earthdata.nasa.gov/search/granules.json",
    "earthdata_login": "https://urs.earthdata.nasa.gov",
    "lp_daac_s3_bucket": "s3://lp-prod-protected/HLSS30_VI.002/",
    "opensearch_api": "https://cmr.earthdata.nasa.gov/opensearch",
    "documentation_url": "https://data.nasa.gov/dataset/hls-sentinel-2-multi-spectral-instrument-vegetation-indices-daily-global-30-m-v2-0-90ed0"
}
with open('/tmp/nasa_hls_package/api_endpoints.json', 'w') as f:
    json.dump(endpoints, f, indent=4)

# 3. Create metadata_summary.json (Vegetation indices)
metadata = {
    "product": "HLSS30_VI",
    "spatial_resolution": "30 meters",
    "grid_system": "Military Grid Reference System (MGRS)",
    "file_format": "Cloud Optimized GeoTIFF (COG)",
    "indices": [
        {"name": "NDVI", "description": "Normalized Difference Vegetation Index"},
        {"name": "EVI", "description": "Enhanced Vegetation Index"},
        {"name": "SAVI", "description": "Soil Adjusted Vegetation Index"},
        {"name": "MSAVI", "description": "Modified Soil Adjusted Vegetation Index"},
        {"name": "NDMI", "description": "Normalized Difference Moisture Index"},
        {"name": "NDWI", "description": "Normalized Difference Water Index"},
        {"name": "NBR", "description": "Normalized Burn Ratio"},
        {"name": "NBR2", "description": "Normalized Burn Ratio 2"},
        {"name": "TVI", "description": "Triangular Vegetation Index"}
    ]
}
with open('/tmp/nasa_hls_package/metadata_summary.json', 'w') as f:
    json.dump(metadata, f, indent=4)

# 4. Create client_example.py
client_code = '''# NASA HLS Data Connector for Antigravity App
# Uses NASA CMR API to query Sentinel-2 Vegetation Indices (HLSS30_VI v2.0)

import requests
import json

CMR_URL = "https://cmr.earthdata.nasa.gov/search/granules.json"

def search_hls_granules(short_name="HLSS30_VI", version="002", polygon=None, temporal=None):
    """
    Search NASA Common Metadata Repository (CMR) for HLS Sentinel-2 granules.
    """
    params = {
        "short_name": short_name,
        "version": version,
        "page_size": 10
    }
    
    if polygon:
        params["polygon"] = polygon
    if temporal:
        params["temporal"] = temporal
        
    response = requests.get(CMR_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        granules = data.get("feed", {}).get("entry", [])
        return granules
    else:
        raise Exception(f"CMR Query failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    print("Searching for recent HLS Sentinel-2 Vegetation Index granules...")
    try:
        # Example bounding polygon or search
        granules = search_hls_granules()
        print(f"Found {len(granules)} granules.")
        for g in granules[:3]:
            print(f"- Title: {g.get('title')}")
            print(f"  Download Link: {g.get('links', [{}])[0].get('href')}")
    except Exception as e:
        print(f"Error: {e}")
'''
with open('/tmp/nasa_hls_package/client_example.py', 'w') as f:
    f.write(client_code)

# 5. Create the zip archive
zip_path = '/tmp/nasa_hls_integration_kit.zip'
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk('/tmp/nasa_hls_package'):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, '/tmp/nasa_hls_package')
            zipf.write(file_path, arcname)

print("ZIP created successfully at:", zip_path)