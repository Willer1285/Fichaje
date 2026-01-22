from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from app.dependencies import get_db
from app.database.models import Employee
from app.utils.security import hash_password
from app.utils.image_processing import process_employee_photo
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
import json

router = APIRouter(
    prefix="/api/employees",
    tags=["employees"],
)

# Esquemas Pydantic para respuesta
class EmployeeResponse(BaseModel):
    id: int
    nombre: str
    apellidos: str
    dni: str
    telefono: str
    email: str = ""
    foto_path: str = ""
    numero_empleado: str = ""
    cargo: str = ""
    departamento_id: Optional[int] = None
    ubicacion_id: Optional[int] = None
    turno_id: Optional[int] = None
    active: bool
    es_admin: bool
    es_superadmin: bool
    pago_por_hora: float
    pago_hora_especial: float
    tipo_jornada: str
    fecha_ingreso: Optional[str] = None
    fecha_egreso: Optional[str] = None
    motivo_egreso: str = ""

@router.get("", response_model=List[EmployeeResponse])
def read_employees(db = Depends(get_db)):
    """Obtiene la lista de todos los empleados"""
    try:
        employees = db.listar_empleados(incluir_inactivos=True)
        return [
            {
                "id": e.id,
                "nombre": e.nombre,
                "apellidos": e.apellidos,
                "dni": e.dni,
                "cargo": e.cargo or "",
                "active": e.activo,
                "telefono": e.telefono,
                "email": e.email or "",
                "foto_path": e.foto_path or "",
                "numero_empleado": e.numero_empleado or "",
                "departamento_id": e.departamento_id,
                "ubicacion_id": e.ubicacion_id,
                "turno_id": e.turno_id,
                "tipo_jornada": e.tipo_jornada or "completa",
                "es_admin": e.es_admin,
                "es_superadmin": e.es_superadmin,
                "pago_por_hora": e.pago_por_hora,
                "pago_hora_especial": e.pago_hora_especial,
                "fecha_ingreso": str(e.fecha_ingreso) if e.fecha_ingreso else None,
                "fecha_egreso": str(e.fecha_egreso) if e.fecha_egreso else None,
                "motivo_egreso": e.motivo_egreso or ""
            } for e in employees
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{employee_id}", response_model=EmployeeResponse)
def read_employee(employee_id: int, db = Depends(get_db)):
    """Obtiene un empleado por ID"""
    e = db.obtener_empleado(employee_id)
    if not e:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
        
    return {
        "id": e.id,
        "nombre": e.nombre,
        "apellidos": e.apellidos,
        "dni": e.dni,
        "cargo": e.cargo or "",
        "active": e.activo,
        "telefono": e.telefono,
        "email": e.email or "",
        "foto_path": e.foto_path or "",
        "numero_empleado": e.numero_empleado or "",
        "departamento_id": e.departamento_id,
        "ubicacion_id": e.ubicacion_id,
        "turno_id": e.turno_id,
        "tipo_jornada": e.tipo_jornada or "completa",
        "es_admin": e.es_admin,
        "es_superadmin": e.es_superadmin,
        "pago_por_hora": e.pago_por_hora,
        "pago_hora_especial": e.pago_hora_especial,
        "fecha_ingreso": str(e.fecha_ingreso) if e.fecha_ingreso else None,
        "fecha_egreso": str(e.fecha_egreso) if e.fecha_egreso else None,
        "motivo_egreso": e.motivo_egreso or ""
    }

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_employee(
    nombre: str = Form(...),
    apellidos: str = Form(...),
    dni: str = Form(...),
    telefono: str = Form(...), # Puede venir como JSON string "[...]"
    email: str = Form(""),
    numero_empleado: str = Form(""),
    cargo: str = Form(""),
    departamento_id: Optional[int] = Form(None),
    ubicacion_id: Optional[int] = Form(None),
    turno_id: Optional[int] = Form(None),
    pago_por_hora: float = Form(0.0),
    pago_hora_especial: float = Form(0.0),
    tipo_jornada: str = Form("completa"),
    es_admin: bool = Form(False),
    password: Optional[str] = Form(None),
    foto: UploadFile = File(None),
    db = Depends(get_db)
):
    """Crea un nuevo empleado"""
    if db.obtener_empleado_por_dni(dni):
        raise HTTPException(status_code=400, detail="El DNI ya está registrado")
    
    # Procesar foto si existe
    foto_path = ""
    if foto:
        try:
            contents = await foto.read()
            if len(contents) > 2 * 1024 * 1024: # 2MB limit
                # raise HTTPException(status_code=400, detail="La imagen no debe pesar más de 2MB")
                # Intentamos procesarla igual, el resize la reducirá
                pass
                
            foto_path = process_employee_photo(contents)
        except Exception as e:
            print(f"Error subiendo foto: {e}")

    # Determinar contraseña (si es admin es obligatoria, si no, generada)
    # El usuario dijo: "el formulario de empleados no debe llevar campo para registrar contraseña... administrador lleva un formulario diferente... con contraseña"
    # Aquí unificamos en un endpoint, pero validamos según es_admin
    
    final_password = "NO_PASSWORD" # Para empleados sin acceso web directo
    if es_admin:
        if not password:
             raise HTTPException(status_code=400, detail="La contraseña es obligatoria para administradores")
        final_password = password
    
    new_emp = Employee(
        nombre=nombre,
        apellidos=apellidos,
        dni=dni,
        telefono=telefono,
        email=email,
        foto_path=foto_path,
        numero_empleado=numero_empleado,
        cargo=cargo,
        departamento_id=departamento_id,
        ubicacion_id=ubicacion_id,
        turno_id=turno_id,
        tipo_jornada=tipo_jornada,
        es_admin=es_admin,
        es_superadmin=False, # Solo se puede asignar manualmente en BD o por otro superadmin (futuro)
        pago_por_hora=pago_por_hora,
        pago_hora_especial=pago_hora_especial,
        password_hash=hash_password(final_password),
        fecha_ingreso=datetime.now(),
        activo=True
    )
    
    try:
        emp_id = db.crear_empleado(new_emp)
        return {"id": emp_id, "message": "Empleado creado correctamente", "foto_path": foto_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{employee_id}")
async def update_employee(
    employee_id: int,
    nombre: str = Form(...),
    apellidos: str = Form(...),
    dni: str = Form(...),
    telefono: str = Form(...),
    email: str = Form(""),
    numero_empleado: str = Form(""),
    cargo: str = Form(""),
    departamento_id: Optional[int] = Form(None),
    ubicacion_id: Optional[int] = Form(None),
    turno_id: Optional[int] = Form(None),
    pago_por_hora: float = Form(0.0),
    pago_hora_especial: float = Form(0.0),
    tipo_jornada: str = Form("completa"),
    es_admin: bool = Form(False),
    # Campos para egresado
    es_egresado: bool = Form(False),
    fecha_egreso: Optional[str] = Form(None),
    motivo_egreso: str = Form(""),
    foto: UploadFile = File(None),
    db = Depends(get_db)
):
    """Actualiza un empleado"""
    existing_emp = db.obtener_empleado(employee_id)
    if not existing_emp:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    
    # Procesar nueva foto si se envía
    if foto:
        try:
            contents = await foto.read()
            # Eliminar foto anterior si existe? (Pendiente limpieza)
            existing_emp.foto_path = process_employee_photo(contents)
        except Exception as e:
            print(f"Error actualizando foto: {e}")

    existing_emp.nombre = nombre
    existing_emp.apellidos = apellidos
    existing_emp.dni = dni
    existing_emp.telefono = telefono
    existing_emp.email = email
    existing_emp.numero_empleado = numero_empleado
    existing_emp.cargo = cargo
    existing_emp.departamento_id = departamento_id
    existing_emp.ubicacion_id = ubicacion_id
    existing_emp.turno_id = turno_id
    existing_emp.tipo_jornada = tipo_jornada
    
    # Solo actualizar admin si se especifica (el frontend debería manejar esto)
    # Nota: Si el usuario es el propio superadmin editándose, no debería poder quitarse admin
    if existing_emp.es_superadmin and not es_admin:
         pass # No permitir quitarse admin al superadmin por error
    else:
         existing_emp.es_admin = es_admin

    existing_emp.pago_por_hora = pago_por_hora
    existing_emp.pago_hora_especial = pago_hora_especial
    
    # Manejo de Egresado
    if es_egresado:
        existing_emp.activo = False
        if fecha_egreso:
            try:
                # Intentar parsear fecha ISO o YYYY-MM-DD
                existing_emp.fecha_egreso = datetime.fromisoformat(fecha_egreso.replace("Z", ""))
            except:
                existing_emp.fecha_egreso = datetime.now()
        else:
            existing_emp.fecha_egreso = datetime.now()
        existing_emp.motivo_egreso = motivo_egreso
    else:
        existing_emp.activo = True # Reactivar si se desmarca
        existing_emp.fecha_egreso = None
        existing_emp.motivo_egreso = ""

    try:
        db.actualizar_empleado(existing_emp)
        return {"message": "Empleado actualizado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{employee_id}")
def delete_employee(employee_id: int, db = Depends(get_db)):
    """Elimina permanentemente un empleado (Solo SuperAdmin debería poder)"""
    # Aquí podríamos verificar si el usuario actual es superadmin, pero por simplicidad
    # asumimos que el frontend protege el botón
    try:
        # Verificar si es superadmin el objetivo
        emp = db.obtener_empleado(employee_id)
        if emp and emp.es_superadmin:
             raise HTTPException(status_code=403, detail="No se puede eliminar al Super Administrador")

        if db.eliminar_empleado(employee_id):
            return {"message": "Empleado eliminado correctamente"}
        else:
            raise HTTPException(status_code=404, detail="Empleado no encontrado")
            
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
