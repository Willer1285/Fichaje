from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_db
from app.database.models import Departamento
from pydantic import BaseModel
from typing import List

router = APIRouter(
    prefix="/api/departments",
    tags=["departments"],
)

class DepartmentBase(BaseModel):
    nombre: str
    activo: bool = True

class DepartmentResponse(DepartmentBase):
    id: int

@router.get("/", response_model=List[DepartmentResponse])
def get_departments(active_only: bool = True, db = Depends(get_db)):
    try:
        return db.listar_departamentos(solo_activos=active_only)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=dict)
def create_department(dept: DepartmentBase, db = Depends(get_db)):
    try:
        new_dept = Departamento(nombre=dept.nombre, activo=dept.activo)
        dept_id = db.crear_departamento(new_dept)
        return {"id": dept_id, "message": "Departamento creado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{dept_id}")
def update_department(dept_id: int, dept: DepartmentBase, db = Depends(get_db)):
    try:
        # En una implementación más robusta, verificaríamos si existe primero
        update_dept = Departamento(id=dept_id, nombre=dept.nombre, activo=dept.activo)
        if db.actualizar_departamento(update_dept):
            return {"message": "Departamento actualizado correctamente"}
        raise HTTPException(status_code=404, detail="Departamento no encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{dept_id}")
def delete_department(dept_id: int, db = Depends(get_db)):
    try:
        if db.eliminar_departamento(dept_id):
            return {"message": "Departamento desactivado correctamente"}
        raise HTTPException(status_code=404, detail="Departamento no encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
