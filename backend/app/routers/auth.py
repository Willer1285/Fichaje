from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.dependencies import get_db
from app.utils.security import verify_password
from app.utils.qr_generator import qr_generator
from app.database.models import Fichaje
from datetime import datetime

router = APIRouter(
    prefix="/api/auth",
    tags=["auth"],
)

class LoginRequest(BaseModel):
    dni: str
    password: str

class EmployeeLoginRequest(BaseModel):
    dni: str
    code: str

@router.get("/qr")
def get_qr_code():
    """Obtiene el código QR actual"""
    if qr_generator.codigo_ha_expirado() or not qr_generator.codigo_actual:
        codigo, imagen = qr_generator.generar_codigo_y_qr()
    else:
        imagen = qr_generator.crear_qr_real(qr_generator.codigo_actual)
        
    return {
        "qr_image": imagen,
        "seconds_left": qr_generator.obtener_tiempo_restante()
    }

@router.post("/login/employee")
def login_employee(data: EmployeeLoginRequest, db = Depends(get_db)):
    """Registra fichaje de empleado usando QR"""
    # 1. Validar código QR
    if not qr_generator.codigo_es_valido(data.code):
        raise HTTPException(status_code=400, detail="Código QR inválido o expirado")
    
    # 2. Validar Empleado
    empleado = db.obtener_empleado_por_dni(data.dni.upper())
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
        
    if not empleado.activo:
         raise HTTPException(status_code=403, detail="Empleado inactivo")
         
    # 3. Registrar Fichaje (Entrada o Salida)
    hoy = datetime.now()
    fichaje_hoy = db.obtener_fichaje_del_dia(empleado.id, hoy)
    
    tipo_accion = "entrada"
    
    # En lugar de fichar automáticamente, devolvemos sesión para el dashboard de empleado
    return {
        "status": "success",
        "access_token": "employee-temp-token", # En producción usar JWT real
        "user": {
            "id": empleado.id,
            "nombre": empleado.nombre,
            "apellidos": empleado.apellidos,
            "foto_path": empleado.foto_path or "",
            "dni": empleado.dni,
            "email": empleado.email or "",
            "tipo_jornada": empleado.tipo_jornada,
            "es_admin": empleado.es_admin
        }
    }

@router.post("/login")
def login(data: LoginRequest, db = Depends(get_db)):
    """Inicia sesión y devuelve el usuario si es correcto"""
    empleado = db.obtener_empleado_por_dni(data.dni.upper())
    
    if not empleado:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
        
    if not verify_password(data.password, empleado.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
        
    if not empleado.activo:
        raise HTTPException(status_code=403, detail="Usuario inactivo")
        
    # Verificar si es admin o superadmin para acceso al dashboard
    if not (empleado.es_admin or empleado.es_superadmin):
        raise HTTPException(status_code=403, detail="Acceso denegado: Se requieren permisos de administrador")

    return {
        "id": empleado.id,
        "nombre": empleado.nombre,
        "apellidos": empleado.apellidos,
        "foto_path": empleado.foto_path or "",
        "dni": empleado.dni,
        "email": empleado.email or "",
        "es_admin": empleado.es_admin,
        "es_superadmin": empleado.es_superadmin,
        "token": "dummy-token-for-now" # En producción usar JWT
    }
