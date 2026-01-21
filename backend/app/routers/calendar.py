from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_db
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/calendar", tags=["calendar"])

@router.get("/events")
def get_calendar_events(start: str, end: str, db = Depends(get_db)):
    """Obtiene eventos para el calendario (fichajes, vacaciones, ausencias)"""
    try:
        # print(f"DEBUG: Calendar events for range {start} to {end}")
        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
        
        events = []
        
        # 1. Fichajes (Llegadas tarde, asistencias)
        fichajes = db.obtener_todos_fichajes_periodo(start_date, end_date)
        # print(f"DEBUG: Calendar - Found {len(fichajes)} checkins")
        turnos = {t.id: t for t in db.listar_turnos()}
        config = db.obtener_configuracion()
        
        for fichaje, empleado in fichajes:
            title = f"Asistencia: {empleado.nombre}"
            color = "#10B981" # Green
            
            # Verificar llegada tarde
            is_late = False
            if fichaje.hora_entrada and empleado.turno_id and empleado.turno_id in turnos:
                turno = turnos[empleado.turno_id]
                try:
                    h, m = map(int, turno.hora_inicio.split(":"))
                    expected = fichaje.hora_entrada.replace(hour=h, minute=m, second=0)
                    limit = expected + timedelta(minutes=config.tiempo_tolerancia_minutos)
                    if fichaje.hora_entrada > limit:
                        is_late = True
                        title = f"Llegada Tarde: {empleado.nombre}"
                        color = "#F59E0B" # Orange
                except:
                    pass
            
            events.append({
                "id": f"fichaje_{fichaje.id}",
                "title": title,
                "start": fichaje.fecha.isoformat(),
                "allDay": True,
                "backgroundColor": color,
                "borderColor": color,
                "extendedProps": {
                    "type": "attendance",
                    "employee": f"{empleado.nombre} {empleado.apellidos}",
                    "late": is_late,
                    "checkIn": fichaje.hora_entrada.strftime("%I:%M %p") if fichaje.hora_entrada else "-"
                }
            })

        # 2. Vacaciones Aprobadas
        # Necesitamos un método para obtener vacaciones por rango de fechas de todos los empleados
        # Como no existe, iteramos empleados activos (no es lo más óptimo pero funciona)
        empleados = db.listar_empleados(incluir_inactivos=False)
        for emp in empleados:
            vacs = db.obtener_solicitudes_empleado(emp.id, incluir_historial=True)
            for v in vacs:
                if v.estado == 'aprobada':
                    # Verificar solapamiento con el rango solicitado
                    if not (v.fecha_fin < start_date or v.fecha_inicio > end_date):
                         events.append({
                            "id": f"vac_{v.id}",
                            "title": f"Vacaciones: {emp.nombre}",
                            "start": v.fecha_inicio.isoformat(),
                            "end": (v.fecha_fin + timedelta(days=1)).isoformat(), # FullCalendar exclusive end
                            "allDay": True,
                            "backgroundColor": "#3B82F6", # Blue
                            "borderColor": "#3B82F6",
                            "extendedProps": {
                                "type": "vacation",
                                "employee": f"{emp.nombre} {emp.apellidos}"
                            }
                        })
            
            # 3. Ausencias
            ausencias = db.obtener_ausencias_empleado(emp.id, incluir_historial=True)
            for a in ausencias:
                if a.estado in ['justificada', 'aprobada']:
                     if not (a.fecha_fin < start_date or a.fecha_inicio > end_date):
                        events.append({
                            "id": f"aus_{a.id}",
                            "title": f"Ausencia: {emp.nombre}",
                            "start": a.fecha_inicio.isoformat(),
                            "end": (a.fecha_fin + timedelta(days=1)).isoformat(),
                            "allDay": True,
                            "backgroundColor": "#EF4444", # Red
                            "borderColor": "#EF4444",
                            "extendedProps": {
                                "type": "absence",
                                "employee": f"{emp.nombre} {emp.apellidos}",
                                "reason": a.tipo_ausencia
                            }
                        })
                        
        return events

    except Exception as e:
        print(f"Error fetching calendar events: {e}")
        return []
