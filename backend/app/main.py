from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routers import employees, attendance, auth, requests, reports, config, departments, locations, schedules, notifications, calendar
from app.utils import paths
import os
import sys
import logging
import time

# Configurar logging si estamos en modo desktop
if getattr(sys, 'frozen', False) or os.environ.get('DESKTOP_MODE'):
    try:
        from app.utils.logger import setup_logging
        setup_logging(log_to_file=True)
        logging.info("📝 Sistema de logging inicializado para modo desktop")
    except Exception as e:
        print(f"⚠️ Error configurando logging en main.py: {e}")

app = FastAPI(title="TimeTrack Pro API", version="2.0.0")

# Middleware para logging de requests (solo en modo desktop/producción)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # Log de request entrante
    if getattr(sys, 'frozen', False) or os.environ.get('DESKTOP_MODE'):
        logging.info(f"📥 {request.method} {request.url.path}")

    response = await call_next(request)

    # Log de response
    duration = time.time() - start_time
    if getattr(sys, 'frozen', False) or os.environ.get('DESKTOP_MODE'):
        status_emoji = "✅" if response.status_code < 400 else "❌"
        logging.info(f"{status_emoji} {request.method} {request.url.path} - Status: {response.status_code} - Duration: {duration:.3f}s")

    return response

# Servir archivos estáticos (uploads)
# Usamos paths.get_uploads_path() que asegura la ruta persistente y crea el directorio
uploads_path = paths.get_uploads_path()
# Montamos la carpeta padre 'assets' para que /assets/uploads/... funcione
# IMPORTANTE: Usar ruta absoluta para evitar que se cree en directorio del .exe
assets_root = os.path.abspath(os.path.dirname(uploads_path))
logging.info(f"📁 Montando archivos estáticos desde: {assets_root}")

# Verificar que el directorio existe antes de montar
if not os.path.exists(assets_root):
    logging.warning(f"⚠️ Creando directorio de assets: {assets_root}")
    os.makedirs(assets_root, exist_ok=True)

app.mount("/assets", StaticFiles(directory=assets_root), name="assets")

# Servir frontend compilado (asegurar que existe la carpeta dist)
frontend_path = paths.get_frontend_dist_path()
if os.path.exists(frontend_path):
    # Montar la raíz de dist en /static para que coincida con base='/static/' de Vite
    app.mount("/static", StaticFiles(directory=frontend_path), name="static_frontend")

# Configuración CORS (Permitir frontend)
origins = [
    "http://localhost:5173", # Vite default
    "http://localhost:3000", # React default
    "*" # Por ahora permitir todo en desarrollo
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth.router)
app.include_router(employees.router)
app.include_router(attendance.router)
app.include_router(requests.router)
app.include_router(reports.router)
app.include_router(config.router)
app.include_router(departments.router)
app.include_router(locations.router)
app.include_router(schedules.router)
app.include_router(notifications.router)
app.include_router(calendar.router)

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

# SPA Fallback - Solo para rutas que NO son API
# Servir index.html para todas las rutas del frontend (SPA routing)
# Esto NO interfiere con /api/* porque esas rutas ya están registradas arriba
@app.exception_handler(404)
async def custom_404_handler(request, __):
    # Si la ruta es de API, devolver JSON 404
    if request.url.path.startswith("/api/"):
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=404, content={"detail": "Not Found"})

    # Para cualquier otra ruta, servir el index.html del SPA
    # frontend_path se define arriba usando paths.get_frontend_dist_path()
    index_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)

    # Si no existe el frontend, devolver mensaje
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=404, content={"message": "Frontend not built"})
