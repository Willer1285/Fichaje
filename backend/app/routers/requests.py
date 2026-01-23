from fastapi import APIRouter, Depends, HTTPException, status
from app.dependencies import get_db
from app.database.models import SolicitudVacacion, Ausencia
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter(
    prefix="/api/requests",
    tags=["requests"],
)

class RequestAction(BaseModel):
    admin_id: int
    reason: Optional[str] = None

class VacationRequest(BaseModel):
    employee_id: int
    fecha_inicio: str
    fecha_fin: str
    tipo: str
    subtipo: Optional[str] = ""
    motivo: Optional[str] = ""

class AbsenceNotification(BaseModel):
    employee_id: int
    fecha_inicio: str
    fecha_fin: str
    tipo: str
    subtipo: Optional[str] = ""
    motivo: str
    impacta_nomina: str

# ==================== EMPLEADO ====================

@router.get("/employee/{employee_id}/vacations")
def get_employee_vacations(employee_id: int, db = Depends(get_db)):
    """Obtiene el historial de vacaciones de un empleado"""
    try:
        solicitudes = db.obtener_solicitudes_empleado(employee_id, incluir_historial=True)
        return [
            {
                "id": s.id,
                "fecha_inicio": s.fecha_inicio.strftime("%Y-%m-%d"),
                "fecha_fin": s.fecha_fin.strftime("%Y-%m-%d"),
                "dias": s.dias_solicitados,
                "tipo": s.tipo,
                "estado": s.estado,
                "motivo": s.motivo_empleado,
                "motivo_rechazo": s.motivo_rechazo
            } for s in solicitudes
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/employee/{employee_id}/vacation-balance/{year}")
def get_vacation_balance(employee_id: int, year: int, db = Depends(get_db)):
    """Obtiene el saldo de vacaciones"""
    try:
        saldo = db.obtener_saldo_vacaciones(employee_id, year)
        return {
            "total": saldo.dias_totales,
            "consumido": saldo.dias_consumidos,
            "pendiente": saldo.dias_pendientes
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/vacations")
def create_vacation_request(data: VacationRequest, db = Depends(get_db)):
    """Crea una nueva solicitud de vacaciones"""
    try:
        fecha_inicio = datetime.strptime(data.fecha_inicio, "%Y-%m-%d")
        fecha_fin = datetime.strptime(data.fecha_fin, "%Y-%m-%d")
        
        # Calcular días laborables
        dias = db.calcular_dias_laborables(fecha_inicio, fecha_fin)
        
        # Validar saldo si es vacación anual
        if data.tipo == "vacaciones_anuales":
            saldo = db.obtener_saldo_vacaciones(data.employee_id, fecha_inicio.year)
            if dias > saldo.dias_pendientes:
                raise HTTPException(status_code=400, detail=f"Saldo insuficiente. Disponibles: {saldo.dias_pendientes}, Solicitados: {dias}")

        solicitud = SolicitudVacacion(
            empleado_id=data.employee_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            dias_solicitados=dias,
            tipo=data.tipo,
            subtipo=data.subtipo,
            estado="pendiente",
            motivo_empleado=data.motivo
        )
        
        db.crear_solicitud_vacacion(solicitud)
        return {"message": "Solicitud enviada correctamente"}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/employee/{employee_id}/absences")
def get_employee_absences(employee_id: int, db = Depends(get_db)):
    """Obtiene el historial de ausencias"""
    try:
        ausencias = db.obtener_ausencias_empleado(employee_id, incluir_historial=True)
        pendientes_justificar = db.obtener_ausencias_pendientes_justificar(employee_id)
        
        return {
            "history": [
                {
                    "id": a.id,
                    "fecha_inicio": a.fecha_inicio.strftime("%Y-%m-%d"),
                    "fecha_fin": a.fecha_fin.strftime("%Y-%m-%d"),
                    "tipo": a.tipo_ausencia,
                    "estado": a.estado,
                    "motivo": a.motivo_empleado
                } for a in ausencias
            ],
            "pending_justification": [
                {
                    "id": p.id,
                    "fecha": p.fecha.strftime("%Y-%m-%d"),
                    "detectada": p.fecha_deteccion.strftime("%Y-%m-%d")
                } for p in pendientes_justificar
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/absences")
def create_absence_notification(data: AbsenceNotification, db = Depends(get_db)):
    """Crea una notificación de ausencia"""
    try:
        ausencia = Ausencia(
            empleado_id=data.employee_id,
            fecha_inicio=datetime.strptime(data.fecha_inicio, "%Y-%m-%d"),
            fecha_fin=datetime.strptime(data.fecha_fin, "%Y-%m-%d"),
            tipo_ausencia=data.tipo,
            subtipo=data.subtipo,
            estado="notificada",
            es_notificacion_previa=True,
            motivo_empleado=data.motivo,
            impacta_nomina=data.impacta_nomina
        )
        db.crear_ausencia(ausencia)
        return {"message": "Ausencia notificada correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ADMIN ====================

@router.get("/vacations")
def get_vacation_requests(db = Depends(get_db)):
    """Obtiene solicitudes de vacaciones pendientes"""
    try:
        solicitudes = db.obtener_solicitudes_pendientes()
        return [
            {
                "id": s.id,
                "empleado": f"{e.nombre} {e.apellidos}",
                "dni": e.dni,
                "fecha_inicio": s.fecha_inicio.strftime("%Y-%m-%d"),
                "fecha_fin": s.fecha_fin.strftime("%Y-%m-%d"),
                "dias": s.dias_solicitados,
                "motivo": s.motivo_empleado,
                "tipo": "Vacaciones"
            } for s, e in solicitudes
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/vacations/{request_id}/approve")
def approve_vacation(request_id: int, action: RequestAction, db = Depends(get_db)):
    """Aprueba una solicitud de vacaciones"""
    try:
        if db.aprobar_solicitud_vacacion(request_id, action.admin_id):
            return {"message": "Solicitud aprobada"}
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/vacations/{request_id}/reject")
def reject_vacation(request_id: int, action: RequestAction, db = Depends(get_db)):
    """Rechaza una solicitud de vacaciones"""
    try:
        if db.rechazar_solicitud_vacacion(request_id, action.admin_id, action.reason or "Sin motivo"):
            return {"message": "Solicitud rechazada"}
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/absences")
def get_absence_requests(db = Depends(get_db)):
    """Obtiene ausencias pendientes de aprobación"""
    try:
        ausencias = db.obtener_ausencias_pendientes_admin()
        return [
            {
                "id": a.id,
                "empleado": f"{e.nombre} {e.apellidos}",
                "dni": e.dni,
                "fecha_inicio": a.fecha_inicio.strftime("%Y-%m-%d"),
                "fecha_fin": a.fecha_fin.strftime("%Y-%m-%d"),
                "tipo_ausencia": a.tipo_ausencia,
                "motivo": a.motivo_empleado,
                "tipo": "Permiso Anticipado" if a.estado == 'notificada' else "Ausencia"
            } for a, e in ausencias
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/absences/{request_id}/approve")
def approve_absence(request_id: int, action: RequestAction, db = Depends(get_db)):
    try:
        if db.aprobar_ausencia(request_id, action.admin_id, action.reason or ""):
            return {"message": "Permiso/Ausencia aprobada"}
        raise HTTPException(status_code=404, detail="Permiso/Ausencia no encontrada")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/absences/{request_id}/reject")
def reject_absence(request_id: int, action: RequestAction, db = Depends(get_db)):
    try:
        if db.rechazar_ausencia(request_id, action.admin_id, action.reason or "Sin motivo"):
            return {"message": "Permiso/Ausencia rechazada"}
        raise HTTPException(status_code=404, detail="Permiso/Ausencia no encontrada")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
