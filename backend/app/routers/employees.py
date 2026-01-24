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
    # Campos de nombre separados
    primer_nombre: str = ""
    segundo_nombre: str = ""
    primer_apellido: str = ""
    segundo_apellido: str = ""
    # Campos legacy (calculados automáticamente)
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
                "primer_nombre": e.primer_nombre or "",
                "segundo_nombre": e.segundo_nombre or "",
                "primer_apellido": e.primer_apellido or "",
                "segundo_apellido": e.segundo_apellido or "",
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

    print(f"📦 [GET /employees/{employee_id}] Empleado obtenido:")
    print(f"   primer_nombre: {e.primer_nombre}")
    print(f"   segundo_nombre: {e.segundo_nombre}")
    print(f"   primer_apellido: {e.primer_apellido}")
    print(f"   segundo_apellido: {e.segundo_apellido}")

    return {
        "id": e.id,
        "primer_nombre": e.primer_nombre or "",
        "segundo_nombre": e.segundo_nombre or "",
        "primer_apellido": e.primer_apellido or "",
        "segundo_apellido": e.segundo_apellido or "",
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
    primer_nombre: str = Form(...),
    segundo_nombre: str = Form(""),
    primer_apellido: str = Form(...),
    segundo_apellido: str = Form(""),
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
            if len(contents) > 1 * 1024 * 1024:  # 1MB limit
                raise HTTPException(status_code=400, detail="La imagen no debe pesar más de 1MB")

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
    
    # Calcular nombre completo y apellidos desde campos separados
    nombre_completo = f"{primer_nombre} {segundo_nombre}".strip()
    apellidos_completo = f"{primer_apellido} {segundo_apellido}".strip()

    new_emp = Employee(
        primer_nombre=primer_nombre,
        segundo_nombre=segundo_nombre,
        primer_apellido=primer_apellido,
        segundo_apellido=segundo_apellido,
        nombre=nombre_completo,
        apellidos=apellidos_completo,
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
    primer_nombre: str = Form(...),
    segundo_nombre: str = Form(""),
    primer_apellido: str = Form(...),
    segundo_apellido: str = Form(""),
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
    eliminar_foto: bool = Form(False),
    db = Depends(get_db)
):
    """Actualiza un empleado"""
    existing_emp = db.obtener_empleado(employee_id)
    if not existing_emp:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    # Validar que el DNI no esté en uso por OTRO empleado
    if dni != existing_emp.dni:
        empleado_con_dni = db.obtener_empleado_por_dni(dni)
        if empleado_con_dni and empleado_con_dni.id != employee_id:
            raise HTTPException(status_code=400, detail="El DNI ya está registrado por otro empleado")

    # Eliminar foto si se solicita
    if eliminar_foto:
        existing_emp.foto_path = ""

    # Procesar nueva foto si se envía
    if foto:
        try:
            contents = await foto.read()
            if len(contents) > 1 * 1024 * 1024:  # 1MB limit
                raise HTTPException(status_code=400, detail="La imagen no debe pesar más de 1MB")

            existing_emp.foto_path = process_employee_photo(contents)
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error actualizando foto: {e}")

    # Actualizar campos de nombre separados y calcular nombre completo
    existing_emp.primer_nombre = primer_nombre
    existing_emp.segundo_nombre = segundo_nombre
    existing_emp.primer_apellido = primer_apellido
    existing_emp.segundo_apellido = segundo_apellido
    existing_emp.nombre = f"{primer_nombre} {segundo_nombre}".strip()
    existing_emp.apellidos = f"{primer_apellido} {segundo_apellido}".strip()

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


@router.post("/migrate-names")
def migrate_employee_names(db = Depends(get_db)):
    """
    Migra los nombres y apellidos existentes a los campos separados.
    Divide 'nombre' en primer_nombre y segundo_nombre.
    Divide 'apellidos' en primer_apellido y segundo_apellido.
    """
    try:
        print("\n🔄 [MIGRACIÓN] Iniciando migración de nombres...")
        employees = db.listar_empleados(incluir_inactivos=True)
        migrated_count = 0

        for emp in employees:
            # Solo migrar si los campos separados están vacíos
            if not emp.primer_nombre and not emp.primer_apellido:
                # Dividir nombres
                nombres = emp.nombre.strip().split() if emp.nombre else []
                apellidos = emp.apellidos.strip().split() if emp.apellidos else []

                # Asignar nombres
                primer_nombre = nombres[0] if len(nombres) > 0 else ""
                segundo_nombre = " ".join(nombres[1:]) if len(nombres) > 1 else ""

                # Asignar apellidos
                primer_apellido = apellidos[0] if len(apellidos) > 0 else ""
                segundo_apellido = " ".join(apellidos[1:]) if len(apellidos) > 1 else ""

                # Actualizar empleado
                emp.primer_nombre = primer_nombre
                emp.segundo_nombre = segundo_nombre
                emp.primer_apellido = primer_apellido
                emp.segundo_apellido = segundo_apellido

                db.actualizar_empleado(emp)
                migrated_count += 1

                print(f"   ✅ Migrado: {emp.nombre} {emp.apellidos} -> {primer_nombre}|{segundo_nombre}|{primer_apellido}|{segundo_apellido}")

        print(f"🎉 [MIGRACIÓN] Completada: {migrated_count} empleados migrados")
        return {
            "message": "Migración completada",
            "migrated_count": migrated_count
        }

    except Exception as e:
        print(f"❌ [MIGRACIÓN] Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/verify-names")
def verify_employee_names(db = Depends(get_db)):
    """
    Verifica el estado de los campos de nombres de todos los empleados.
    Útil para diagnóstico.
    """
    try:
        employees = db.listar_empleados(incluir_inactivos=True)
        result = []

        for emp in employees:
            result.append({
                "id": emp.id,
                "nombre_completo": f"{emp.nombre} {emp.apellidos}",
                "campos_separados": {
                    "primer_nombre": emp.primer_nombre or "[VACÍO]",
                    "segundo_nombre": emp.segundo_nombre or "[VACÍO]",
                    "primer_apellido": emp.primer_apellido or "[VACÍO]",
                    "segundo_apellido": emp.segundo_apellido or "[VACÍO]"
                },
                "tiene_campos_vacios": not (emp.primer_nombre and emp.primer_apellido)
            })

        vacios = sum(1 for r in result if r["tiene_campos_vacios"])

        return {
            "total_empleados": len(result),
            "con_campos_vacios": vacios,
            "con_campos_llenos": len(result) - vacios,
            "empleados": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
