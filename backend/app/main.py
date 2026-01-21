from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers import employees, attendance, auth, requests, reports, config, departments, locations, schedules, notifications, calendar
import os

app = FastAPI(title="TimeTrack Pro API", version="2.0.0")

# Servir archivos estáticos (uploads)
# Asegurar que el directorio existe
os.makedirs("assets/uploads", exist_ok=True)
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

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

@app.get("/")
def read_root():
    return {"message": "Welcome to TimeTrack Pro API", "status": "online"}

@app.get("/api/health")
def health_check():
    return {"status": "ok"}
