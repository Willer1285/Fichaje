from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.dependencies import get_db
from app.utils.security import verify_password
from app.utils.qr_generator import qr_generator
from app.database.models import Fichaje
from datetime import datetime
import logging

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
    logging.info("\n🔐 [LOGIN] Intento de inicio de sesión:")
    logging.info(f"   DNI recibido: '{data.dni}'")
    logging.info(f"   DNI normalizado: '{data.dni.upper()}'")

    empleado = db.obtener_empleado_por_dni(data.dni.upper())

    if not empleado:
        logging.info(f"❌ [LOGIN] No se encontró empleado con DNI: {data.dni.upper()}")
        logging.info("   Verificando empleados existentes en la base de datos...")
        # Listar todos los empleados para diagnóstico
        try:
            todos = db.listar_empleados(incluir_inactivos=True)
            logging.info(f"   Total empleados en BD: {len(todos)}")
            for emp in todos[:5]:  # Mostrar primeros 5
                logging.info(f"     - DNI: {emp.dni}, Nombre: {emp.nombre} {emp.apellidos}, Activo: {emp.activo}")
        except Exception as e:
            logging.info(f"   Error al listar empleados: {e}")
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    logging.info("✓ [LOGIN] Empleado encontrado:")
    logging.info(f"   ID: {empleado.id}")
    logging.info(f"   Nombre: {empleado.nombre} {empleado.apellidos}")
    logging.info(f"   DNI: {empleado.dni}")
    logging.info(f"   Activo: {empleado.activo}")
    logging.info(f"   Es admin: {empleado.es_admin}")
    logging.info(f"   Es superadmin: {empleado.es_superadmin}")
    logging.info(f"   Password hash: {empleado.password_hash[:20]}... (longitud: {len(empleado.password_hash)})")

    if not verify_password(data.password, empleado.password_hash):
        logging.info(f"❌ [LOGIN] Contraseña incorrecta para DNI: {data.dni.upper()}")
        logging.info(f"   Contraseña recibida: '{data.password}' (longitud: {len(data.password)})")
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    logging.info("✓ [LOGIN] Contraseña verificada correctamente")

    if not empleado.activo:
        logging.info(f"❌ [LOGIN] Usuario inactivo: {empleado.dni}")
        raise HTTPException(status_code=403, detail="Usuario inactivo")

    # Verificar si es admin o superadmin para acceso al dashboard
    if not (empleado.es_admin or empleado.es_superadmin):
        logging.info(f"❌ [LOGIN] Usuario sin permisos de administrador: {empleado.dni}")
        raise HTTPException(status_code=403, detail="Acceso denegado: Se requieren permisos de administrador")

    logging.info(f"✅ [LOGIN] Inicio de sesión exitoso para: {empleado.nombre} {empleado.apellidos}")
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
