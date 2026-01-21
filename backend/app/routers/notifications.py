from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_db
from datetime import datetime

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

@router.get("/admin")
def get_admin_notifications(db = Depends(get_db)):
    try:
        # Get pending requests
        pending = db.obtener_solicitudes_pendientes()
        absences = db.obtener_ausencias_pendientes_admin()
        
        notifs = []
        for req, emp in pending:
            notifs.append({
                "id": f"req_{req.id}",
                "title": "Nueva Solicitud",
                "desc": f"{emp.nombre} solicita vacaciones",
                "time": req.fecha_solicitud.strftime("%I:%M %p") if req.fecha_solicitud else "",
                "type": "info",
                "link": "requests"
            })
            
        for aus, emp in absences:
            notifs.append({
                "id": f"aus_{aus.id}",
                "title": "Ausencia a revisar",
                "desc": f"{emp.nombre} - {aus.tipo_ausencia}",
                "time": aus.fecha_registro.strftime("%I:%M %p") if aus.fecha_registro else "",
                "type": "warning",
                "link": "requests"
            })
            
        return notifs
    except Exception as e:
        print(f"Error fetching notifications: {e}")
        return []

@router.get("/alerts")
def get_dashboard_alerts(db = Depends(get_db)):
    """Obtiene alertas detalladas para el dashboard (Llegadas tarde, ausencias, etc)"""
    try:
        hoy = datetime.now()
        inicio_dia = hoy.replace(hour=0, minute=0, second=0)
        fin_dia = hoy.replace(hour=23, minute=59, second=59)

        alerts = []

        # 1. Llegadas tarde de HOY
        fichajes_hoy = db.obtener_todos_fichajes_periodo(inicio_dia, fin_dia)
        turnos = {t.id: t for t in db.listar_turnos()}
        config = db.obtener_configuracion()

        for fichaje, empleado in fichajes_hoy:
            if not fichaje.hora_entrada: continue

            hora_inicio_esperada = None
            if empleado.turno_id and empleado.turno_id in turnos:
                turno = turnos[empleado.turno_id]
                try:
                    h, m = map(int, turno.hora_inicio.split(":"))
                    hora_inicio_esperada = fichaje.hora_entrada.replace(hour=h, minute=m, second=0)
                except:
                    continue
            else:
                continue

            limite = hora_inicio_esperada + datetime.timedelta(minutes=config.tiempo_tolerancia_minutos)

            if fichaje.hora_entrada > limite:
                diff = fichaje.hora_entrada - hora_inicio_esperada
                minutos_tarde = int(diff.total_seconds() / 60)
                alerts.append({
                    "id": f"late_{fichaje.id}",
                    "type": "warning",
                    "title": "Llegada Tarde",
                    "message": f"{empleado.nombre} {empleado.apellidos} llegó {minutos_tarde} min tarde",
                    "time": fichaje.hora_entrada.strftime("%I:%M %p"),
                    "details": {
                        "empleado": f"{empleado.nombre} {empleado.apellidos}",
                        "empleado_id": empleado.id,
                        "dni": empleado.dni,
                        "departamento": empleado.cargo or "N/A",
                        "hora_llegada": fichaje.hora_entrada.strftime("%I:%M %p"),
                        "hora_esperada": hora_inicio_esperada.strftime("%I:%M %p"),
                        "minutos_tarde": minutos_tarde,
                        "fecha": fichaje.fecha.strftime("%Y-%m-%d")
                    }
                })

        # 2. Empleados que NO han fichado hoy (ausentes sin justificar)
        empleados_activos = db.listar_empleados(incluir_inactivos=False)
        empleados_con_fichaje = set(f.empleado_id for f, _ in fichajes_hoy)

        for emp in empleados_activos:
            if emp.id not in empleados_con_fichaje:
                # Verificar si tiene una justificación previa (ausencia o vacaciones aprobadas)
                ausencias = db.obtener_ausencias_empleado(emp.id, incluir_historial=True)
                vacaciones = db.obtener_solicitudes_empleado(emp.id, incluir_historial=True)

                tiene_justificacion = False

                # Verificar ausencias del día
                for aus in ausencias:
                    if aus.fecha_inicio.date() <= hoy.date() <= aus.fecha_fin.date():
                        if aus.estado in ['justificada', 'aprobada']:
                            tiene_justificacion = True
                            break

                # Verificar vacaciones del día
                if not tiene_justificacion:
                    for vac in vacaciones:
                        if vac.fecha_inicio.date() <= hoy.date() <= vac.fecha_fin.date():
                            if vac.estado == 'aprobada':
                                tiene_justificacion = True
                                break

                # Si no tiene justificación, agregar alerta
                if not tiene_justificacion:
                    alerts.append({
                        "id": f"absent_{emp.id}",
                        "type": "error",
                        "title": "Ausencia sin Justificar",
                        "message": f"{emp.nombre} {emp.apellidos} no ha fichado hoy",
                        "time": hoy.strftime("%I:%M %p"),
                        "details": {
                            "empleado": f"{emp.nombre} {emp.apellidos}",
                            "empleado_id": emp.id,
                            "dni": emp.dni,
                            "departamento": emp.cargo or "N/A",
                            "fecha": hoy.strftime("%Y-%m-%d"),
                            "turno": turnos[emp.turno_id].nombre if emp.turno_id and emp.turno_id in turnos else "Sin turno asignado"
                        }
                    })

        # Ordenar por tiempo (más recientes primero)
        alerts.sort(key=lambda x: x['time'], reverse=True)

        return alerts

    except Exception as e:
        print(f"Error fetching alerts: {e}")
        import traceback
        traceback.print_exc()
        return []

@router.get("/alert/{alert_id}")
def get_alert_details(alert_id: str, db = Depends(get_db)):
    """Obtiene detalles completos de una alerta específica"""
    try:
        # El alert_id tiene formato: "late_{fichaje_id}" o "absent_{empleado_id}"
        parts = alert_id.split("_")
        alert_type = parts[0]
        entity_id = int(parts[1])

        hoy = datetime.now()

        if alert_type == "late":
            # Buscar fichaje
            fichaje = db.obtener_fichaje_por_id(entity_id)
            if not fichaje:
                raise HTTPException(status_code=404, detail="Fichaje no encontrado")

            empleado = db.obtener_empleado(fichaje.empleado_id)
            turno = db.obtener_turno(empleado.turno_id) if empleado.turno_id else None
            config = db.obtener_configuracion()

            # Calcular detalles de retraso
            hora_inicio_esperada = None
            minutos_tarde = 0
            if turno and fichaje.hora_entrada:
                try:
                    h, m = map(int, turno.hora_inicio.split(":"))
                    hora_inicio_esperada = fichaje.hora_entrada.replace(hour=h, minute=m, second=0)
                    limite = hora_inicio_esperada + datetime.timedelta(minutes=config.tiempo_tolerancia_minutos)
                    if fichaje.hora_entrada > limite:
                        diff = fichaje.hora_entrada - hora_inicio_esperada
                        minutos_tarde = int(diff.total_seconds() / 60)
                except:
                    pass

            return {
                "id": alert_id,
                "type": "warning",
                "title": "Llegada Tarde - Detalles Completos",
                "empleado": {
                    "id": empleado.id,
                    "nombre": f"{empleado.nombre} {empleado.apellidos}",
                    "dni": empleado.dni,
                    "numero_empleado": empleado.numero_empleado,
                    "email": empleado.email,
                    "telefono": empleado.telefono,
                    "cargo": empleado.cargo,
                    "departamento": empleado.cargo or "N/A"
                },
                "fichaje": {
                    "fecha": fichaje.fecha.strftime("%Y-%m-%d"),
                    "hora_entrada": fichaje.hora_entrada.strftime("%I:%M %p") if fichaje.hora_entrada else "N/A",
                    "hora_salida": fichaje.hora_salida.strftime("%I:%M %p") if fichaje.hora_salida else "Aún trabajando",
                    "tipo": fichaje.tipo_fichaje,
                    "observaciones": fichaje.observaciones or "Sin observaciones"
                },
                "retraso": {
                    "hora_esperada": hora_inicio_esperada.strftime("%I:%M %p") if hora_inicio_esperada else "N/A",
                    "hora_llegada": fichaje.hora_entrada.strftime("%I:%M %p") if fichaje.hora_entrada else "N/A",
                    "minutos_tarde": minutos_tarde,
                    "tolerancia": config.tiempo_tolerancia_minutos
                },
                "turno": {
                    "nombre": turno.nombre if turno else "Sin turno",
                    "hora_inicio": turno.hora_inicio if turno else "N/A",
                    "hora_fin": turno.hora_fin if turno else "N/A"
                }
            }

        elif alert_type == "absent":
            # Empleado ausente
            empleado = db.obtener_empleado(entity_id)
            if not empleado:
                raise HTTPException(status_code=404, detail="Empleado no encontrado")

            turno = db.obtener_turno(empleado.turno_id) if empleado.turno_id else None

            # Buscar si hay ausencias pendientes
            ausencias_pendientes = db.obtener_ausencias_pendientes_justificar(entity_id)

            return {
                "id": alert_id,
                "type": "error",
                "title": "Ausencia sin Justificar - Detalles Completos",
                "empleado": {
                    "id": empleado.id,
                    "nombre": f"{empleado.nombre} {empleado.apellidos}",
                    "dni": empleado.dni,
                    "numero_empleado": empleado.numero_empleado,
                    "email": empleado.email,
                    "telefono": empleado.telefono,
                    "cargo": empleado.cargo,
                    "departamento": empleado.cargo or "N/A"
                },
                "ausencia": {
                    "fecha": hoy.strftime("%Y-%m-%d"),
                    "turno_esperado": turno.nombre if turno else "Sin turno",
                    "hora_inicio_esperada": turno.hora_inicio if turno else "N/A",
                    "dias_pendientes": len(ausencias_pendientes),
                    "ultimo_fichaje": "Información no disponible"  # Se puede mejorar agregando un método en db_manager
                },
                "turno": {
                    "nombre": turno.nombre if turno else "Sin turno",
                    "hora_inicio": turno.hora_inicio if turno else "N/A",
                    "hora_fin": turno.hora_fin if turno else "N/A"
                }
            }

        else:
            raise HTTPException(status_code=400, detail="Tipo de alerta no válido")

    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error fetching alert details: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/employee/{employee_id}")
def get_employee_notifications(employee_id: int, db = Depends(get_db)):
    try:
        requests = db.obtener_solicitudes_empleado(employee_id, incluir_historial=True)
        absences = db.obtener_ausencias_empleado(employee_id, incluir_historial=True)
        
        all_items = []
        for r in requests:
            if r.estado in ['aprobada', 'rechazada']:
                all_items.append({
                    "id": f"vac_{r.id}",
                    "title": f"Vacaciones {r.estado}",
                    "desc": f"Tu solicitud ha sido {r.estado}",
                    "date": r.fecha_respuesta or datetime.now(),
                    "type": "success" if r.estado == 'aprobada' else "error"
                })
                
        for a in absences:
            if a.estado in ['aprobada', 'rechazada']:
                all_items.append({
                    "id": f"abs_{a.id}",
                    "title": f"Ausencia {a.estado}",
                    "desc": f"Justificación {a.estado}",
                    "date": a.fecha_aprobacion or datetime.now(),
                    "type": "success" if a.estado == 'aprobada' else "error"
                })
                
        # Sort by date desc
        all_items.sort(key=lambda x: x['date'], reverse=True)
        
        # Format date for frontend
        result = []
        for item in all_items[:5]:
            result.append({
                "id": item['id'],
                "title": item['title'],
                "desc": item['desc'],
                "time": item['date'].strftime("%d/%m"),
                "type": item['type']
            })
            
        return result
    except Exception as e:
        print(f"Error fetching employee notifications: {e}")
        return []
