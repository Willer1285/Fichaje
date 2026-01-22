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
    """Obtiene todas las actividades del día para mostrar en Alertas del Día"""
    try:
        hoy = datetime.now()
        inicio_dia = hoy.replace(hour=0, minute=0, second=0)
        fin_dia = hoy.replace(hour=23, minute=59, second=59)

        alerts = []

        # Obtener todos los fichajes de HOY
        fichajes_hoy = db.obtener_todos_fichajes_periodo(inicio_dia, fin_dia)
        turnos = {t.id: t for t in db.listar_turnos()}
        config = db.obtener_configuracion()
        todos_empleados = db.listar_empleados(incluir_inactivos=False)

        # 0. NUEVOS EMPLEADOS
        for emp in todos_empleados:
            if emp.fecha_alta and emp.fecha_alta.date() == hoy.date():
                alerts.append({
                    "id": f"new_emp_{emp.id}",
                    "type": "info",
                    "title": "Nuevo Empleado",
                    "message": f"Se ha registrado a {emp.nombre} {emp.apellidos}",
                    "time": emp.fecha_alta.strftime("%I:%M %p"),
                    "details": None
                })

        # 0.5 CAMBIOS EN EL SISTEMA (Modificaciones)
        try:
            modificaciones = db.obtener_modificaciones_recientes(hoy)
            for mod in modificaciones:
                campo = mod.get('campo_modificado', 'datos')
                nombre = f"{mod.get('nombre', '')} {mod.get('apellidos', '')}"
                alerts.append({
                    "id": f"mod_{mod.get('id')}",
                    "type": "info",
                    "title": "Cambio en Sistema",
                    "message": f"Cambio de {campo} en {nombre}",
                    "time": "Hoy",
                    "details": None
                })
        except Exception:
            pass # Si falla el historial, continuar

        # 1. FICHAJES COMPLETADOS (tipo success/verde)
        # 2. LLEGADAS TARDE (tipo warning/amarillo)
        for fichaje, empleado in fichajes_hoy:
            # Excluir administradores de alertas de fichaje
            if empleado.es_admin or empleado.es_superadmin:
                continue

            if not fichaje.hora_entrada:
                continue

            # Si el fichaje está completo (tiene salida)
            if fichaje.hora_salida:
                # Calcular si llegó tarde
                es_tarde = False
                minutos_tarde = 0

                if empleado.turno_id and empleado.turno_id in turnos:
                    turno = turnos[empleado.turno_id]
                    try:
                        h, m = map(int, turno.hora_inicio.split(":"))
                        hora_inicio_esperada = fichaje.hora_entrada.replace(hour=h, minute=m, second=0)
                        limite = hora_inicio_esperada + datetime.timedelta(minutes=config.tiempo_tolerancia_minutos)

                        if fichaje.hora_entrada > limite:
                            es_tarde = True
                            diff = fichaje.hora_entrada - hora_inicio_esperada
                            minutos_tarde = int(diff.total_seconds() / 60)
                    except:
                        pass

                # Alerta de fichaje completado
                alerts.append({
                    "id": f"completed_{fichaje.id}",
                    "type": "success",
                    "title": "Fichaje completado",
                    "message": f"{empleado.nombre} {empleado.apellidos} finalizó su jornada",
                    "time": fichaje.hora_salida.strftime("%I:%M %p"),
                    "details": {
                        "empleado": f"{empleado.nombre} {empleado.apellidos}",
                        "hora_entrada": fichaje.hora_entrada.strftime("%I:%M %p"),
                        "hora_salida": fichaje.hora_salida.strftime("%I:%M %p"),
                        "es_tarde": es_tarde,
                        "minutos_tarde": minutos_tarde if es_tarde else 0
                    }
                })

            # Si llegó tarde (independiente de si completó o no)
            if empleado.turno_id and empleado.turno_id in turnos:
                turno = turnos[empleado.turno_id]
                try:
                    h, m = map(int, turno.hora_inicio.split(":"))
                    hora_inicio_esperada = fichaje.hora_entrada.replace(hour=h, minute=m, second=0)
                    limite = hora_inicio_esperada + datetime.timedelta(minutes=config.tiempo_tolerancia_minutos)

                    if fichaje.hora_entrada > limite:
                        diff = fichaje.hora_entrada - hora_inicio_esperada
                        minutos_tarde = int(diff.total_seconds() / 60)
                        alerts.append({
                            "id": f"late_{fichaje.id}",
                            "type": "warning",
                            "title": "Retraso registrado",
                            "message": f"{empleado.nombre} {empleado.apellidos} - {minutos_tarde} min tarde",
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
                except:
                    pass

        # 3. AUSENCIAS SIN JUSTIFICAR (tipo error/rojo)
        empleados_con_fichaje = set(f.empleado_id for f, _ in fichajes_hoy)

        for emp in todos_empleados:
            # Excluir administradores de alertas de ausencia
            if emp.es_admin or emp.es_superadmin:
                continue

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
                    # Calcular hora esperada de entrada
                    hora_esperada_str = "Hora desconocida"
                    mostrar_alerta = True

                    if emp.turno_id and emp.turno_id in turnos:
                        turno = turnos[emp.turno_id]
                        hora_esperada_str = turno.hora_inicio
                        
                        try:
                            # Validar tolerancia de 2 horas para marcar ausencia
                            h, m = map(int, turno.hora_inicio.split(":"))
                            hora_inicio_turno = hoy.replace(hour=h, minute=m, second=0, microsecond=0)
                            
                            # Si el turno es más tarde en el día
                            if hoy < hora_inicio_turno:
                                mostrar_alerta = False
                            else:
                                # Han pasado menos de 2 horas (7200 segundos)
                                diferencia = (hoy - hora_inicio_turno).total_seconds()
                                if diferencia < 7200: 
                                    mostrar_alerta = False
                        except:
                            pass

                    if mostrar_alerta:
                        alerts.append({
                            "id": f"absent_{emp.id}",
                            "type": "error",
                            "title": "Ausencia sin justificar",
                            "message": f"{emp.nombre} {emp.apellidos} no ha fichado hoy",
                            "time": hora_esperada_str,
                            "details": {
                                "empleado": f"{emp.nombre} {emp.apellidos}",
                                "empleado_id": emp.id,
                                "dni": emp.dni,
                                "departamento": emp.cargo or "N/A",
                                "fecha": hoy.strftime("%Y-%m-%d"),
                                "turno": turnos[emp.turno_id].nombre if emp.turno_id and emp.turno_id in turnos else "Sin turno asignado"
                            }
                        })

        # 4. SOLICITUDES Y APROBACIONES DE VACACIONES/PERMISOS
        for emp in todos_empleados:
            # Excluir administradores de solicitudes
            if emp.es_admin or emp.es_superadmin:
                continue

            solicitudes = db.obtener_solicitudes_empleado(emp.id, incluir_historial=True)
            for solicitud in solicitudes:
                # 4.1 Solicitudes CREADAS hoy
                if solicitud.fecha_solicitud and solicitud.fecha_solicitud.date() == hoy.date():
                    alerts.append({
                        "id": f"request_{solicitud.id}",
                        "type": "info",
                        "title": "Nueva solicitud",
                        "message": f"{emp.nombre} {emp.apellidos} solicitó {solicitud.tipo.replace('_', ' ')}",
                        "time": solicitud.fecha_solicitud.strftime("%I:%M %p") if solicitud.fecha_solicitud else "Hoy",
                        "details": {
                            "empleado": f"{emp.nombre} {emp.apellidos}",
                            "tipo": solicitud.tipo.replace("_", " ").title(),
                            "fecha_inicio": solicitud.fecha_inicio.strftime("%Y-%m-%d"),
                            "fecha_fin": solicitud.fecha_fin.strftime("%Y-%m-%d"),
                            "dias": solicitud.dias_solicitados,
                            "estado": solicitud.estado
                        }
                    })

                # 4.2 Solicitudes APROBADAS o RECHAZADAS hoy
                elif solicitud.fecha_respuesta and solicitud.fecha_respuesta.date() == hoy.date():
                    if solicitud.estado == "aprobada":
                        alerts.append({
                            "id": f"approved_{solicitud.id}",
                            "type": "success",
                            "title": "Solicitud aprobada",
                            "message": f"{emp.nombre} {emp.apellidos} - {solicitud.tipo.replace('_', ' ')} aprobado",
                            "time": solicitud.fecha_respuesta.strftime("%I:%M %p"),
                            "details": {
                                "empleado": f"{emp.nombre} {emp.apellidos}",
                                "tipo": solicitud.tipo.replace("_", " ").title(),
                                "fecha_inicio": solicitud.fecha_inicio.strftime("%Y-%m-%d"),
                                "fecha_fin": solicitud.fecha_fin.strftime("%Y-%m-%d"),
                                "dias": solicitud.dias_solicitados,
                                "estado": "Aprobada",
                                "aprobado_por": solicitud.aprobado_por or "Administrador"
                            }
                        })
                    elif solicitud.estado == "rechazada":
                        alerts.append({
                            "id": f"rejected_{solicitud.id}",
                            "type": "error",
                            "title": "Solicitud rechazada",
                            "message": f"{emp.nombre} {emp.apellidos} - {solicitud.tipo.replace('_', ' ')} rechazado",
                            "time": solicitud.fecha_respuesta.strftime("%I:%M %p"),
                            "details": {
                                "empleado": f"{emp.nombre} {emp.apellidos}",
                                "tipo": solicitud.tipo.replace("_", " ").title(),
                                "fecha_inicio": solicitud.fecha_inicio.strftime("%Y-%m-%d"),
                                "fecha_fin": solicitud.fecha_fin.strftime("%Y-%m-%d"),
                                "motivo": solicitud.motivo_rechazo or "Sin motivo especificado",
                                "rechazado_por": solicitud.aprobado_por or "Administrador"
                            }
                        })

                # 4.3 Solicitudes PENDIENTES (además de las de hoy)
                elif solicitud.estado == 'pendiente':
                    tipo_str = solicitud.tipo.replace("_", " ").title()
                    alerts.append({
                        "id": f"request_pending_{solicitud.id}",
                        "type": "info",
                        "title": f"Solicitud pendiente: {tipo_str}",
                        "message": f"{emp.nombre} {emp.apellidos} - pendiente",
                        "time": solicitud.fecha_solicitud.strftime("%I:%M %p") if solicitud.fecha_solicitud else "Hoy",
                        "details": {
                            "empleado": f"{emp.nombre} {emp.apellidos}",
                            "tipo": tipo_str,
                            "fecha_inicio": solicitud.fecha_inicio.strftime("%Y-%m-%d"),
                            "fecha_fin": solicitud.fecha_fin.strftime("%Y-%m-%d"),
                            "dias": solicitud.dias_solicitados,
                            "estado": "pendiente"
                        }
                    })

            # 5. AUSENCIAS JUSTIFICADAS registradas HOY
            ausencias = db.obtener_ausencias_empleado(emp.id, incluir_historial=True)
            for ausencia in ausencias:
                # Ausencias registradas hoy
                if ausencia.fecha_registro and ausencia.fecha_registro.date() == hoy.date():
                    alerts.append({
                        "id": f"absence_registered_{ausencia.id}",
                        "type": "info",
                        "title": "Ausencia registrada",
                        "message": f"{emp.nombre} {emp.apellidos} registró ausencia: {ausencia.tipo_ausencia}",
                        "time": ausencia.fecha_registro.strftime("%I:%M %p"),
                        "details": {
                            "empleado": f"{emp.nombre} {emp.apellidos}",
                            "tipo": ausencia.tipo_ausencia,
                            "fecha_inicio": ausencia.fecha_inicio.strftime("%Y-%m-%d"),
                            "fecha_fin": ausencia.fecha_fin.strftime("%Y-%m-%d"),
                            "motivo": ausencia.motivo_empleado or "Sin motivo",
                            "estado": ausencia.estado
                        }
                    })

                # Ausencias APROBADAS o JUSTIFICADAS hoy
                elif ausencia.fecha_aprobacion and ausencia.fecha_aprobacion.date() == hoy.date():
                    if ausencia.estado in ['justificada', 'aprobada']:
                        alerts.append({
                            "id": f"absence_approved_{ausencia.id}",
                            "type": "success",
                            "title": "Ausencia justificada",
                            "message": f"{emp.nombre} {emp.apellidos} - Ausencia aprobada",
                            "time": ausencia.fecha_aprobacion.strftime("%I:%M %p"),
                            "details": {
                                "empleado": f"{emp.nombre} {emp.apellidos}",
                                "tipo": ausencia.tipo_ausencia,
                                "fecha_inicio": ausencia.fecha_inicio.strftime("%Y-%m-%d"),
                                "fecha_fin": ausencia.fecha_fin.strftime("%Y-%m-%d"),
                                "motivo": ausencia.motivo_empleado or "Sin motivo"
                            }
                        })

        # Limitar a máximo 20 alertas
        alerts.sort(key=lambda x: x.get('time', ''), reverse=True) # Ordenar por hora (simple string sort, podría mejorarse)
        alerts_limitadas = alerts[:20]

        return alerts_limitadas

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
                    "ultimo_fichaje": "Información no disponible"
                },
                "turno": {
                    "nombre": turno.nombre if turno else "Sin turno",
                    "hora_inicio": turno.hora_inicio if turno else "N/A",
                    "hora_fin": turno.hora_fin if turno else "N/A"
                }
            }

        elif alert_type == "completed":
            # Fichaje completado
            fichaje = db.obtener_fichaje_por_id(entity_id)
            if not fichaje:
                raise HTTPException(status_code=404, detail="Fichaje no encontrado")

            empleado = db.obtener_empleado(fichaje.empleado_id)
            turno = db.obtener_turno(empleado.turno_id) if empleado.turno_id else None

            return {
                "id": alert_id,
                "type": "success",
                "title": "Fichaje Completado - Detalles Completos",
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
                    "hora_salida": fichaje.hora_salida.strftime("%I:%M %p") if fichaje.hora_salida else "N/A",
                    "horas_trabajadas": round(fichaje.horas_trabajadas, 2) if fichaje.horas_trabajadas else 0,
                    "tipo": fichaje.tipo_fichaje,
                    "observaciones": fichaje.observaciones or "Sin observaciones"
                },
                "turno": {
                    "nombre": turno.nombre if turno else "Sin turno",
                    "hora_inicio": turno.hora_inicio if turno else "N/A",
                    "hora_fin": turno.hora_fin if turno else "N/A"
                }
            }

        elif alert_type == "request":
            # Solicitud de vacaciones/cambio
            solicitud = db.obtener_solicitud_por_id(entity_id)
            if not solicitud:
                raise HTTPException(status_code=404, detail="Solicitud no encontrada")

            empleado = db.obtener_empleado(solicitud.empleado_id)

            return {
                "id": alert_id,
                "type": "info",
                "title": "Solicitud de Cambio - Detalles Completos",
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
                "solicitud": {
                    "tipo": solicitud.tipo.replace("_", " ").title(),
                    "fecha_inicio": solicitud.fecha_inicio.strftime("%Y-%m-%d"),
                    "fecha_fin": solicitud.fecha_fin.strftime("%Y-%m-%d"),
                    "dias_solicitados": solicitud.dias_solicitados,
                    "estado": solicitud.estado,
                    "motivo": solicitud.motivo_empleado or "Sin motivo especificado",
                    "fecha_solicitud": solicitud.fecha_solicitud.strftime("%Y-%m-%d %I:%M %p") if solicitud.fecha_solicitud else "N/A"
                }
            }

        elif alert_type == "approved":
            # Solicitud aprobada
            solicitud = db.obtener_solicitud_por_id(entity_id)
            if not solicitud:
                raise HTTPException(status_code=404, detail="Solicitud no encontrada")

            empleado = db.obtener_empleado(solicitud.empleado_id)

            return {
                "id": alert_id,
                "type": "success",
                "title": "Solicitud Aprobada - Detalles Completos",
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
                "solicitud": {
                    "tipo": solicitud.tipo.replace("_", " ").title(),
                    "fecha_inicio": solicitud.fecha_inicio.strftime("%Y-%m-%d"),
                    "fecha_fin": solicitud.fecha_fin.strftime("%Y-%m-%d"),
                    "dias_solicitados": solicitud.dias_solicitados,
                    "estado": "Aprobada",
                    "motivo": solicitud.motivo_empleado or "Sin motivo especificado",
                    "fecha_aprobacion": solicitud.fecha_respuesta.strftime("%Y-%m-%d %I:%M %p") if solicitud.fecha_respuesta else "N/A",
                    "aprobado_por": solicitud.aprobado_por or "Administrador"
                }
            }

        elif alert_type == "rejected":
            # Solicitud rechazada
            solicitud = db.obtener_solicitud_por_id(entity_id)
            if not solicitud:
                raise HTTPException(status_code=404, detail="Solicitud no encontrada")

            empleado = db.obtener_empleado(solicitud.empleado_id)

            return {
                "id": alert_id,
                "type": "error",
                "title": "Solicitud Rechazada - Detalles Completos",
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
                "solicitud": {
                    "tipo": solicitud.tipo.replace("_", " ").title(),
                    "fecha_inicio": solicitud.fecha_inicio.strftime("%Y-%m-%d"),
                    "fecha_fin": solicitud.fecha_fin.strftime("%Y-%m-%d"),
                    "dias_solicitados": solicitud.dias_solicitados,
                    "estado": "Rechazada",
                    "motivo_solicitud": solicitud.motivo_empleado or "Sin motivo",
                    "motivo_rechazo": solicitud.motivo_rechazo or "Sin motivo especificado",
                    "fecha_rechazo": solicitud.fecha_respuesta.strftime("%Y-%m-%d %I:%M %p") if solicitud.fecha_respuesta else "N/A",
                    "rechazado_por": solicitud.aprobado_por or "Administrador"
                }
            }

        elif alert_type == "absence":
            # Parse para distinguir entre "absence_registered" y "absence_approved"
            # Si el alert_id tiene más partes, extraer el subtipo
            if len(parts) > 2:
                absence_subtype = parts[1]  # "registered" o "approved"
                absence_id = int(parts[2])
            else:
                # Compatibilidad con formato antiguo
                absence_id = entity_id
                absence_subtype = "registered"

            ausencia = db.obtener_ausencia_por_id(absence_id)
            if not ausencia:
                raise HTTPException(status_code=404, detail="Ausencia no encontrada")

            empleado = db.obtener_empleado(ausencia.empleado_id)

            return {
                "id": alert_id,
                "type": "info" if absence_subtype == "registered" else "success",
                "title": f"Ausencia {'Registrada' if absence_subtype == 'registered' else 'Aprobada'} - Detalles Completos",
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
                    "tipo": ausencia.tipo_ausencia,
                    "fecha_inicio": ausencia.fecha_inicio.strftime("%Y-%m-%d"),
                    "fecha_fin": ausencia.fecha_fin.strftime("%Y-%m-%d"),
                    "motivo": ausencia.motivo_empleado or "Sin motivo especificado",
                    "estado": ausencia.estado,
                    "fecha_registro": ausencia.fecha_registro.strftime("%Y-%m-%d %I:%M %p") if ausencia.fecha_registro else "N/A",
                    "fecha_aprobacion": ausencia.fecha_aprobacion.strftime("%Y-%m-%d %I:%M %p") if ausencia.fecha_aprobacion else "N/A"
                }
            }

        elif alert_type == "new":
            # Nuevo empleado (format: "new_employee_{id}" or "new_emp_{id}")
            if len(parts) > 2:
                if parts[1] in ["employee", "emp"]:
                    emp_id = int(parts[2])
                else:
                    emp_id = entity_id
            else:
                emp_id = entity_id

            empleado = db.obtener_empleado(emp_id)
            if not empleado:
                raise HTTPException(status_code=404, detail="Empleado no encontrado")

            turno = db.obtener_turno(empleado.turno_id) if empleado.turno_id else None
            tipo_usuario = "Administrador" if (empleado.es_admin or empleado.es_superadmin) else "Empleado"

            return {
                "id": alert_id,
                "type": "info",
                "title": f"Nuevo {tipo_usuario} - Detalles Completos",
                "empleado": {
                    "id": empleado.id,
                    "nombre": f"{empleado.nombre} {empleado.apellidos}",
                    "dni": empleado.dni,
                    "numero_empleado": empleado.numero_empleado,
                    "email": empleado.email,
                    "telefono": empleado.telefono,
                    "cargo": empleado.cargo or "Sin cargo",
                    "departamento": empleado.cargo or "N/A",
                    "tipo": tipo_usuario,
                    "fecha_alta": empleado.fecha_alta.strftime("%Y-%m-%d") if empleado.fecha_alta else "N/A"
                },
                "turno": {
                    "nombre": turno.nombre if turno else "Sin turno asignado",
                    "hora_inicio": turno.hora_inicio if turno else "N/A",
                    "hora_fin": turno.hora_fin if turno else "N/A"
                }
            }

        elif alert_type == "mod":
            # Modificación del sistema
            # No tenemos una tabla de modificaciones individual, así que retornar info básica
            return {
                "id": alert_id,
                "type": "info",
                "title": "Cambio en Sistema - Detalles",
                "message": "Se realizó un cambio en el sistema. Ver historial de modificaciones para más detalles."
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
