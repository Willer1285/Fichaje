from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from app.dependencies import get_db
from app.database.models import Configuracion
from pydantic import BaseModel
from typing import Optional
import os
import uuid
from pathlib import Path

router = APIRouter(
    prefix="/api/config",
    tags=["config"],
)

UPLOAD_DIR = Path("assets/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def save_upload(file: UploadFile) -> str:
    try:
        # Generar nombre único manteniendo extensión
        ext = os.path.splitext(file.filename)[1]
        filename = f"{uuid.uuid4()}{ext}"
        file_path = UPLOAD_DIR / filename
        
        with open(file_path, "wb") as buffer:
            import shutil
            shutil.copyfileobj(file.file, buffer)
            
        return f"/assets/uploads/{filename}"
    except Exception as e:
        print(f"Error guardando archivo: {e}")
        return ""

@router.get("")
def get_config(db = Depends(get_db)):
    try:
        config = db.obtener_configuracion()
        return {
            "nombre_aplicacion": config.nombre_aplicacion,
            "nombre_empresa": config.nombre_empresa,
            "representante_legal": config.representante_legal,
            "dni_cif": config.dni_cif,
            "direccion": config.direccion,
            "ciudad": config.ciudad,
            "codigo_postal": config.codigo_postal,
            "pais": config.pais,
            "telefono_empresa": config.telefono_empresa,
            "email_empresa": config.email_empresa,
            "logo_path": config.logo_path,
            "icono_path": config.icono_path,
            "clave_aprobacion_horas_extras": config.clave_aprobacion_horas_extras,
            "permitir_llegadas_tarde": config.permitir_llegadas_tarde,
            "tiempo_tolerancia_horas": config.tiempo_tolerancia_horas,
            "tiempo_tolerancia_minutos": config.tiempo_tolerancia_minutos,
            "zona_horaria": config.zona_horaria,
            "moneda": config.moneda
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("")
def update_config(
    nombre_aplicacion: Optional[str] = Form(None),
    nombre_empresa: Optional[str] = Form(None),
    representante_legal: Optional[str] = Form(None),
    dni_cif: Optional[str] = Form(None),
    direccion: Optional[str] = Form(None),
    ciudad: Optional[str] = Form(None),
    codigo_postal: Optional[str] = Form(None),
    pais: Optional[str] = Form(None),
    telefono_empresa: Optional[str] = Form(None),
    email_empresa: Optional[str] = Form(None),
    clave_aprobacion_horas_extras: Optional[str] = Form(None),
    permitir_llegadas_tarde: Optional[bool] = Form(None),
    tiempo_tolerancia_horas: Optional[int] = Form(None),
    tiempo_tolerancia_minutos: Optional[int] = Form(None),
    zona_horaria: Optional[str] = Form(None),
    moneda: Optional[str] = Form(None),
    logo: UploadFile = File(None),
    icono: UploadFile = File(None),
    db = Depends(get_db)
):
    try:
        config = db.obtener_configuracion()
        
        # Actualizar campos si se envían (los Forms envían None si no están)
        # Nota: Si el frontend envía string "null" o vacío para borrar, hay que manejarlo.
        # Aquí asumimos que se envía el valor actual si no se cambia.
        
        if nombre_aplicacion is not None: config.nombre_aplicacion = nombre_aplicacion
        if nombre_empresa is not None: config.nombre_empresa = nombre_empresa
        if representante_legal is not None: config.representante_legal = representante_legal
        if dni_cif is not None: config.dni_cif = dni_cif
        if direccion is not None: config.direccion = direccion
        if ciudad is not None: config.ciudad = ciudad
        if codigo_postal is not None: config.codigo_postal = codigo_postal
        if pais is not None: config.pais = pais
        if telefono_empresa is not None: config.telefono_empresa = telefono_empresa
        if email_empresa is not None: config.email_empresa = email_empresa
        if clave_aprobacion_horas_extras is not None: config.clave_aprobacion_horas_extras = clave_aprobacion_horas_extras
        if permitir_llegadas_tarde is not None: config.permitir_llegadas_tarde = permitir_llegadas_tarde
        if tiempo_tolerancia_horas is not None: config.tiempo_tolerancia_horas = tiempo_tolerancia_horas
        if tiempo_tolerancia_minutos is not None: config.tiempo_tolerancia_minutos = tiempo_tolerancia_minutos
        if zona_horaria is not None: config.zona_horaria = zona_horaria
        if moneda is not None: config.moneda = moneda
        
        # Procesar archivos
        if logo:
            path = save_upload(logo)
            if path: config.logo_path = path
            
        if icono:
            path = save_upload(icono)
            if path: config.icono_path = path
        
        if db.actualizar_configuracion(config):
            return {"message": "Configuración actualizada correctamente"}
        else:
            raise HTTPException(status_code=500, detail="No se pudo actualizar la configuración")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
