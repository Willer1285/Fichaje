from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_db
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/calendar", tags=["calendar"])

@router.get("/events")
def get_calendar_events(start: str, end: str, db = Depends(get_db)):
    """Obtiene eventos para el calendario (fichajes, vacaciones, ausencias)"""
    try:
        print(f"\n📅 [GET /calendar/events] Solicitando eventos para rango {start} a {end}")
        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
        print(f"   start_date (datetime): {start_date}")
        print(f"   end_date (datetime): {end_date}")

        events = []

        # 1. Fichajes (Llegadas tarde, asistencias)
        fichajes = db.obtener_todos_fichajes_periodo(start_date, end_date)
        print(f"✅ [Calendar] Fichajes encontrados: {len(fichajes)}")

        if len(fichajes) > 0:
            print(f"   Primer fichaje: fecha={fichajes[0][0].fecha}, empleado={fichajes[0][1].nombre}")

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
            
            # Formatear fecha solo como YYYY-MM-DD
            fecha_str = fichaje.fecha.strftime("%Y-%m-%d") if hasattr(fichaje.fecha, 'strftime') else str(fichaje.fecha).split('T')[0]

            event = {
                "id": f"fichaje_{fichaje.id}",
                "title": title,
                "start": fecha_str,
                "allDay": True,
                "backgroundColor": color,
                "borderColor": color,
                "extendedProps": {
                    "type": "attendance",
                    "employee": f"{empleado.nombre} {empleado.apellidos}",
                    "late": is_late,
                    "checkIn": fichaje.hora_entrada.strftime("%I:%M %p") if fichaje.hora_entrada else "-"
                }
            }

            if len(events) == 0:  # Solo logear el primer evento
                print(f"   📌 Primer evento creado: id={event['id']}, start={event['start']}, title={event['title']}")

            events.append(event)

        # 2. Vacaciones (TODAS - pendientes, aprobadas, rechazadas)
        # Necesitamos un método para obtener vacaciones por rango de fechas de todos los empleados
        # Como no existe, iteramos empleados activos (no es lo más óptimo pero funciona)
        empleados = db.listar_empleados(incluir_inactivos=False)
        for emp in empleados:
            vacs = db.obtener_solicitudes_empleado(emp.id, incluir_historial=True)
            for v in vacs:
                # Verificar solapamiento con el rango solicitado
                if not (v.fecha_fin < start_date or v.fecha_inicio > end_date):
                    # Colores según estado
                    color_map = {
                        'pendiente': '#F59E0B',  # Amber - Pending
                        'aprobada': '#3B82F6',   # Blue - Approved
                        'rechazada': '#EF4444'   # Red - Rejected
                    }
                    color = color_map.get(v.estado, '#6B7280')  # Gray default

                    # Título más descriptivo
                    estado_label = {
                        'pendiente': 'Pendiente',
                        'aprobada': 'Aprobada',
                        'rechazada': 'Rechazada'
                    }.get(v.estado, v.estado.capitalize())

                    tipo_label = {
                        'vacaciones_anuales': 'Vacaciones',
                        'permiso_retribuido': 'Permiso Retribuido',
                        'permiso_sin_sueldo': 'Permiso Sin Sueldo'
                    }.get(v.tipo_solicitud, 'Vacaciones')

                    events.append({
                        "id": f"vac_{v.id}",
                        "title": f"{tipo_label} ({estado_label}): {emp.nombre}",
                        "start": v.fecha_inicio.isoformat(),
                        "end": (v.fecha_fin + timedelta(days=1)).isoformat(), # FullCalendar exclusive end
                        "allDay": True,
                        "backgroundColor": color,
                        "borderColor": color,
                        "extendedProps": {
                            "type": "vacation",
                            "employee": f"{emp.nombre} {emp.apellidos}",
                            "estado": v.estado,
                            "tipo_solicitud": v.tipo_solicitud,
                            "subtipo": v.subtipo or "N/A",
                            "motivo": v.motivo or ""
                        }
                    })
            
            # 3. Ausencias (TODAS - notificadas, pendientes, justificadas, aprobadas, rechazadas)
            ausencias = db.obtener_ausencias_empleado(emp.id, incluir_historial=True)
            for a in ausencias:
                if not (a.fecha_fin < start_date or a.fecha_inicio > end_date):
                    # Colores según tipo de ausencia y estado
                    if a.estado == 'rechazada':
                        color = '#DC2626'  # Dark Red - Rejected
                    elif a.estado in ['notificada', 'pendiente_justificar']:
                        # Estados pendientes - colores más claros
                        tipo_color_map = {
                            'baja_medica': '#C4B5FD',        # Light Purple
                            'permiso_retribuido': '#A7F3D0',  # Light Green
                            'permiso_no_retribuido': '#FED7AA', # Light Orange
                            'ausencia_injustificada': '#FECACA' # Light Red
                        }
                        color = tipo_color_map.get(a.tipo_ausencia, '#D1D5DB')  # Light Gray default
                    else:  # justificada, aprobada
                        # Estados confirmados - colores normales
                        tipo_color_map = {
                            'baja_medica': '#8B5CF6',        # Purple - Medical Leave
                            'permiso_retribuido': '#10B981',  # Green - Paid Permission
                            'permiso_no_retribuido': '#F97316', # Orange - Unpaid Permission
                            'ausencia_injustificada': '#EF4444' # Red - Unjustified
                        }
                        color = tipo_color_map.get(a.tipo_ausencia, '#6B7280')  # Gray default

                    # Etiquetas descriptivas
                    tipo_label_map = {
                        'baja_medica': 'Baja Médica',
                        'permiso_retribuido': 'Permiso Retribuido',
                        'permiso_no_retribuido': 'Permiso No Retribuido',
                        'ausencia_injustificada': 'Ausencia Injustificada'
                    }
                    tipo_label = tipo_label_map.get(a.tipo_ausencia, a.tipo_ausencia.replace('_', ' ').title())

                    estado_label_map = {
                        'notificada': 'Notificada',
                        'pendiente_justificar': 'Pendiente Justificar',
                        'justificada': 'Justificada',
                        'aprobada': 'Aprobada',
                        'rechazada': 'Rechazada'
                    }
                    estado_label = estado_label_map.get(a.estado, a.estado.capitalize())

                    events.append({
                        "id": f"aus_{a.id}",
                        "title": f"{tipo_label} ({estado_label}): {emp.nombre}",
                        "start": a.fecha_inicio.isoformat(),
                        "end": (a.fecha_fin + timedelta(days=1)).isoformat(),
                        "allDay": True,
                        "backgroundColor": color,
                        "borderColor": color,
                        "extendedProps": {
                            "type": "absence",
                            "employee": f"{emp.nombre} {emp.apellidos}",
                            "reason": a.tipo_ausencia,
                            "estado": a.estado,
                            "tipo_ausencia": a.tipo_ausencia,
                            "subtipo": a.subtipo or "N/A",
                            "motivo": a.motivo or ""
                        }
                    })

        print(f"📊 [Calendar] Total eventos devueltos: {len(events)}")
        if len(events) > 0:
            print(f"   Primer evento: {events[0]}")

        return events

    except Exception as e:
        print(f"❌ Error fetching calendar events: {e}")
        import traceback
        traceback.print_exc()
        return []
