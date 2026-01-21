from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_db
from app.database.models import Turno
from pydantic import BaseModel
from typing import List

router = APIRouter(
    prefix="/api/schedules",
    tags=["schedules"],
)

class ScheduleBase(BaseModel):
    nombre: str
    dias_semana: str # "Lunes,Martes,..."
    hora_inicio: str # "09:00"
    hora_fin: str # "17:00"
    activo: bool = True

class ScheduleResponse(ScheduleBase):
    id: int

@router.get("/", response_model=List[ScheduleResponse])
def get_schedules(active_only: bool = True, db = Depends(get_db)):
    try:
        return db.listar_turnos(solo_activos=active_only)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=dict)
def create_schedule(schedule: ScheduleBase, db = Depends(get_db)):
    try:
        new_turno = Turno(
            nombre=schedule.nombre,
            dias_semana=schedule.dias_semana,
            hora_inicio=schedule.hora_inicio,
            hora_fin=schedule.hora_fin,
            activo=schedule.activo
        )
        turno_id = db.crear_turno(new_turno)
        return {"id": turno_id, "message": "Horario creado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{schedule_id}")
def update_schedule(schedule_id: int, schedule: ScheduleBase, db = Depends(get_db)):
    try:
        update_turno = Turno(
            id=schedule_id,
            nombre=schedule.nombre,
            dias_semana=schedule.dias_semana,
            hora_inicio=schedule.hora_inicio,
            hora_fin=schedule.hora_fin,
            activo=schedule.activo
        )
        if db.actualizar_turno(update_turno):
            return {"message": "Horario actualizado correctamente"}
        raise HTTPException(status_code=404, detail="Horario no encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{schedule_id}")
def delete_schedule(schedule_id: int, db = Depends(get_db)):
    try:
        if db.eliminar_turno(schedule_id):
            return {"message": "Horario desactivado correctamente"}
        raise HTTPException(status_code=404, detail="Horario no encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
