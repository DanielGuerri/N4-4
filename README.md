# PastureRestore V2

Mini proyecto NASA Space Apps 2026.

## Qué hace esta versión

- El usuario dibuja un polígono sobre el mapa.
- El frontend envía el polígono GeoJSON a una API propia.
- La API autentica contra Copernicus Data Space.
- La API consulta Sentinel-2 L2A mediante Statistical API.
- Se calcula NDVI real con B04 (rojo) y B08 (infrarrojo cercano).
- Se toma el último resultado diario válido dentro de los últimos 30 días.
- El resultado se muestra en el menú principal y en la zona.

El porcentaje mostrado es una representación visual del NDVI normalizado entre 0 y 1 para esta demo; no debe interpretarse como porcentaje científico de cobertura o salud del pastizal.

## Estructura

```text
pasturerestore-v2/
├── index.html
├── README.md
└── api/
    ├── main.py
    ├── requirements.txt
    ├── .env.example
    └── .gitignore
```

## Desarrollo local

### 1. Frontend

Abrir `index.html` con Live Server en VS Code.

Por defecto la app busca la API en:

`http://127.0.0.1:8000`

Si cambiás la API, modificar `API_BASE_URL` al comienzo del JavaScript de `index.html`.

### 2. API

En VS Code:

```powershell
cd api
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Copiar `.env.example` a `.env` y completar las credenciales de Copernicus.

Luego:

```powershell
$env:COPERNICUS_CLIENT_ID="TU_CLIENT_ID"
$env:COPERNICUS_CLIENT_SECRET="TU_CLIENT_SECRET"
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Prueba:

`http://127.0.0.1:8000/api/health`

## Credenciales

No subir nunca `CLIENT_SECRET` a GitHub.

Crear un OAuth Client en Copernicus Data Space y guardar el secreto como variable de entorno del servidor.

## Despliegue

Frontend: GitHub Pages.

API: Render como Web Service.

### Render

Root Directory:

`api`

Build Command:

```text
pip install -r requirements.txt
```

Start Command:

```text
uvicorn main:app --host 0.0.0.0 --port $PORT
```

Variables:

```text
COPERNICUS_CLIENT_ID=...
COPERNICUS_CLIENT_SECRET=...
ALLOWED_ORIGINS=https://TU_USUARIO.github.io
```

Después de obtener la URL de Render, por ejemplo:

`https://pasturerestore-api.onrender.com`

cambiar en `index.html`:

```javascript
const API_BASE_URL = 'https://pasturerestore-api.onrender.com';
```

y volver a subir el cambio a GitHub.

## Flujo GitHub del equipo

Seguir el circuito acordado:

1. `git pull origin main`
2. Crear rama, por ejemplo `feature/sentinel-ndvi`
3. Hacer cambios
4. Commit
5. Push
6. Pull Request
7. Revisión
8. Merge a `main`
9. Borrar la rama
10. Volver a `main` y hacer `git pull`

## Fuente de datos

Copernicus Data Space / Sentinel-2 L2A / Sentinel Hub Statistical API.
