Set-Location "$PSScriptRoot\api"
if (!(Test-Path ".venv")) {
    python -m venv .venv
}
if (!(Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Archivo .env creado a partir de .env.example. Recorda configurar tus credenciales si vas a consultar Sentinel-2." -ForegroundColor Yellow
}
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
& ".\.venv\Scripts\python.exe" -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
