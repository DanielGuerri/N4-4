Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "       Iniciando PastureRestore (N4-4)        " -ForegroundColor Cyan
Write-Host "   Satélite Primario: Copernicus Sentinel-2   " -ForegroundColor Cyan
Write-Host "   Satélite Respaldo: NASA HLS (HLSS30_VI)    " -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan

$apiDir = Join-Path $PSScriptRoot "api"
Set-Location $apiDir

if (!(Test-Path ".venv")) {
    Write-Host "Creando entorno virtual Python..." -ForegroundColor Yellow
    python -m venv .venv
}

if (!(Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Archivo .env creado a partir de .env.example." -ForegroundColor Yellow
}

Write-Host "Verificando librerias (FastAPI, GDAL, Rasterio, NumPy)..." -ForegroundColor Gray
& ".\.venv\Scripts\python.exe" -m pip install -q -r requirements.txt

# Abrir el navegador en 2 segundos
Start-Job -ScriptBlock {
    Start-Sleep -Seconds 2
    Start-Process "http://127.0.0.1:8000"
} | Out-Null

Write-Host ""
Write-Host ">> Servidor web y satelital activo en: http://127.0.0.1:8000" -ForegroundColor Green
Write-Host ">> Abriendo tu navegador web automaticamente..." -ForegroundColor Green
Write-Host ">> Presiona Ctrl + C en esta ventana cuando quieras detenerlo." -ForegroundColor DarkGray
Write-Host ""

& ".\.venv\Scripts\python.exe" -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
