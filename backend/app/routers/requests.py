from fastapi import APIRouter, Depends, HTTPException, status
from app.dependencies import get_db
from app.database.models import SolicitudVacacion, Ausencia
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta

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
    es_por_horas: bool = False
    horas_solicitadas: float = 0.0

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
            
            # Obtener solicitudes pendientes para restar del saldo disponible
            pendientes = db.obtener_solicitudes_empleado(data.employee_id, solo_pendientes=True)
            dias_pendientes = sum(p.dias_solicitados for p in pendientes if p.tipo == "vacaciones_anuales")
            
            total_solicitado = dias + dias_pendientes
            
            if total_solicitado > saldo.dias_pendientes:
                raise HTTPException(status_code=400, detail=f"Saldo insuficiente. Disponibles: {saldo.dias_pendientes}, En trámite: {dias_pendientes}, Solicitados ahora: {dias}. Total excedente: {total_solicitado - saldo.dias_pendientes}")

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
                    "motivo": a.motivo_empleado,
                    "motivo_rechazo": a.observaciones_admin if a.estado == 'rechazada' else None,
                    "observaciones_admin": a.observaciones_admin,
                    "es_por_horas": a.es_por_horas,
                    "horas_solicitadas": a.horas_solicitadas
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
        # Validar permisos por horas
        if data.es_por_horas:
            if data.horas_solicitadas <= 0:
                raise HTTPException(status_code=400, detail="La cantidad de horas debe ser mayor a 0")
            
            # Obtener empleado para verificar jornada
            empleado = db.obtener_empleado(data.employee_id)
            if not empleado:
                raise HTTPException(status_code=404, detail="Empleado no encontrado")
            
            horas_jornada = 8.0 # Valor por defecto
            
            if empleado.turno_id:
                turno = db.obtener_turno(empleado.turno_id)
                if turno and turno.hora_inicio and turno.hora_fin:
                    try:
                        h_ini, m_ini = map(int, turno.hora_inicio.split(':'))
                        h_fin, m_fin = map(int, turno.hora_fin.split(':'))
                        inicio = timedelta(hours=h_ini, minutes=m_ini)
                        fin = timedelta(hours=h_fin, minutes=m_fin)
                        
                        # Manejar turno nocturno
                        if fin <= inicio:
                            fin += timedelta(days=1)
                            
                        duracion = (fin - inicio).total_seconds() / 3600
                        horas_jornada = duracion
                    except:
                        pass # Usar default si hay error parseando
            
            limite_horas = horas_jornada / 2
            if data.horas_solicitadas > limite_horas:
                raise HTTPException(status_code=400, detail=f"Las horas solicitadas ({data.horas_solicitadas}) no pueden exceder la mitad de la jornada ({limite_horas} horas)")

        ausencia = Ausencia(
            empleado_id=data.employee_id,
            fecha_inicio=datetime.strptime(data.fecha_inicio, "%Y-%m-%d"),
            fecha_fin=datetime.strptime(data.fecha_fin, "%Y-%m-%d"),
            tipo_ausencia=data.tipo,
            subtipo=data.subtipo,
            estado="notificada",
            es_notificacion_previa=True,
            motivo_empleado=data.motivo,
            impacta_nomina=data.impacta_nomina,
            es_por_horas=data.es_por_horas,
            horas_solicitadas=data.horas_solicitadas
        )
        db.crear_ausencia(ausencia)
        return {"message": "Permiso notificado correctamente"}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ADMIN ====================

@router.get("/vacations")
def get_vacation_requests(status: Optional[str] = 'pendiente', db = Depends(get_db)):
    """Obtiene solicitudes de vacaciones filtradas por estado (pendiente por defecto)"""
    try:
        solicitudes = db.obtener_solicitudes_vacaciones_admin(status)
        return [
            {
                "id": s.id,
                "empleado": f"{e.nombre} {e.apellidos}",
                "dni": e.dni,
                "fecha_inicio": s.fecha_inicio.strftime("%Y-%m-%d"),
                "fecha_fin": s.fecha_fin.strftime("%Y-%m-%d"),
                "dias": s.dias_solicitados,
                "motivo": s.motivo_empleado,
                "tipo": "Vacaciones",
                "estado": s.estado,
                "motivo_rechazo": s.motivo_rechazo
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

@router.delete("/vacations/{request_id}")
def delete_vacation_request(request_id: int, db = Depends(get_db)):
    """Elimina una solicitud de vacaciones"""
    try:
        if db.eliminar_solicitud_vacacion(request_id):
            return {"message": "Solicitud eliminada"}
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/absences")
def get_absence_requests(status: Optional[str] = 'pendiente', db = Depends(get_db)):
    """Obtiene ausencias filtradas por estado (pendiente por defecto)"""
    try:
        ausencias = db.obtener_ausencias_admin(status)
        return [
            {
                "id": a.id,
                "empleado": f"{e.nombre} {e.apellidos}",
                "dni": e.dni,
                "fecha_inicio": a.fecha_inicio.strftime("%Y-%m-%d"),
                "fecha_fin": a.fecha_fin.strftime("%Y-%m-%d"),
                "tipo_ausencia": a.tipo_ausencia,
                "motivo": a.motivo_empleado,
                "tipo": "Permiso Anticipado" if a.estado == 'notificada' else "Ausencia",
                "estado": a.estado,
                "observaciones_admin": a.observaciones_admin
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

@router.delete("/absences/{request_id}")
def delete_absence_request(request_id: int, db = Depends(get_db)):
    """Elimina una solicitud de ausencia"""
    try:
        if db.eliminar_ausencia(request_id):
            return {"message": "Solicitud eliminada"}
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
