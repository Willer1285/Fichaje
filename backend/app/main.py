from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routers import employees, attendance, auth, requests, reports, config, departments, locations, schedules, notifications, calendar
import os

app = FastAPI(title="TimeTrack Pro API", version="2.0.0")

# Servir archivos estáticos (uploads)
os.makedirs("assets/uploads", exist_ok=True)
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

# Servir frontend compilado (asegurar que existe la carpeta dist)
frontend_path = os.path.join(os.getcwd(), "frontend", "dist")
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

# SPA Fallback - Servir index.html para cualquier ruta no capturada por la API
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    # Si la ruta comienza con /api, dejar que FastAPI maneje el 404 si no existe
    if full_path.startswith("api"):
        return {"detail": "Not Found"}
    
    # Servir archivos estáticos raíz si existen (favicon, etc)
    potential_file = os.path.join(frontend_path, full_path)
    if os.path.exists(potential_file) and os.path.isfile(potential_file):
        return FileResponse(potential_file)

    # Si no, servir index.html
    return FileResponse(os.path.join(frontend_path, "index.html"))
