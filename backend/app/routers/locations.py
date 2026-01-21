from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_db
from app.database.models import Ubicacion
from pydantic import BaseModel
from typing import List

router = APIRouter(
    prefix="/api/locations",
    tags=["locations"],
)

class LocationBase(BaseModel):
    nombre: str
    activo: bool = True

class LocationResponse(LocationBase):
    id: int

@router.get("/", response_model=List[LocationResponse])
def get_locations(active_only: bool = True, db = Depends(get_db)):
    try:
        return db.listar_ubicaciones(solo_activos=active_only)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=dict)
def create_location(loc: LocationBase, db = Depends(get_db)):
    try:
        new_loc = Ubicacion(nombre=loc.nombre, activo=loc.activo)
        loc_id = db.crear_ubicacion(new_loc)
        return {"id": loc_id, "message": "Ubicación creada correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{loc_id}")
def update_location(loc_id: int, loc: LocationBase, db = Depends(get_db)):
    try:
        update_loc = Ubicacion(id=loc_id, nombre=loc.nombre, activo=loc.activo)
        if db.actualizar_ubicacion(update_loc):
            return {"message": "Ubicación actualizada correctamente"}
        raise HTTPException(status_code=404, detail="Ubicación no encontrada")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{loc_id}")
def delete_location(loc_id: int, db = Depends(get_db)):
    try:
        if db.eliminar_ubicacion(loc_id):
            return {"message": "Ubicación desactivada correctamente"}
        raise HTTPException(status_code=404, detail="Ubicación no encontrada")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
