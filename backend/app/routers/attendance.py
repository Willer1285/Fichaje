from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from app.dependencies import get_db
from app.database.models import Fichaje, Turno, Ausencia
from datetime import datetime, timedelta, date
from typing import Optional, List
from pydantic import BaseModel
import json

router = APIRouter(
    prefix="/api/attendance",
    tags=["attendance"],
)

class ClockAction(BaseModel):
    employee_id: int
    action: str  # "entry", "exit", "break_start", "break_end"
    type: Optional[str] = "normal"
    pin: Optional[str] = None

class JustificationData(BaseModel):
    employee_id: int
    tipo: str
    motivo: str
    fecha_inicio: str # YYYY-MM-DD
    fecha_fin: str # YYYY-MM-DD
    documento: Optional[str] = None

def detect_absences(employee_id: int, db):
    """Detecta ausencias automáticas basándose en el último fichaje"""
    try:
        hoy = datetime.now().date()
        
        # Buscar el último fichaje registrado en la historia
        ultimo_fichaje = db.obtener_ultimo_fichaje(employee_id)
        
        ultima_fecha = None
        if ultimo_fichaje:
             ultima_fecha = ultimo_fichaje.fecha.date()
        else:
             # Si no hay fichajes, usar fecha de ingreso o fecha de alta
             empleado = db.obtener_empleado(employee_id)
             if empleado:
                 if empleado.fecha_ingreso:
                     ultima_fecha = empleado.fecha_ingreso.date()
                 elif empleado.fecha_alta:
                     ultima_fecha = empleado.fecha_alta.date()
        
        # Si no hay fecha de referencia o es hoy/futuro, no hay ausencias pasadas
        if not ultima_fecha or ultima_fecha >= hoy:
            return

        fecha_iter = ultima_fecha + timedelta(days=1)
        ausencias_registradas = db.obtener_ausencias_empleado(employee_id, incluir_historial=True)
        
        while fecha_iter < hoy:
            if fecha_iter.weekday() < 5: # Simplificación: L-V
                tiene_justificacion = any(
                    aus.fecha_inicio.date() <= fecha_iter <= aus.fecha_fin.date()
                    for aus in ausencias_registradas
                )
                if not tiene_justificacion:
                    db.crear_ausencia_pendiente(employee_id, datetime.combine(fecha_iter, datetime.min.time()))
            fecha_iter += timedelta(days=1)
    except Exception as e:
        print(f"Error detectando ausencias: {e}")

def process_auto_checkout(db):
    """Cierra automáticamente fichajes olvidados"""
    try:
        # 1. Obtener todos los fichajes abiertos de AYER hacia atrás
        # (Para hoy se maneja diferente para no cerrar antes de tiempo si hay horas extra)
        # Aquí simplificamos: cerramos todo lo que esté abierto y sea anterior a hoy
        
        # Como no hay método directo "obtener_abiertos", iteramos empleados activos
        # Esto podría optimizarse con una consulta SQL directa, pero usamos los métodos del db_manager por seguridad
        
        hoy = datetime.now()
        ayer = hoy - timedelta(days=1)
        
        # Obtener fichajes de ayer (que deberían estar cerrados)
        # Nota: Idealmente iterar un rango más amplio si el script no corre a diario
        inicio_rev = ayer - timedelta(days=5) # Revisar últimos 5 días
        fichajes_recientes = db.obtener_todos_fichajes_periodo(inicio_rev, hoy) # Incluye hoy para revisar turnos terminados
        
        turnos = {t.id: t for t in db.listar_turnos()}
        
        count = 0
        for fichaje, empleado in fichajes_recientes:
            if fichaje.hora_salida:
                continue # Ya cerrado
            
            # Si es de una fecha anterior a hoy, cerrar seguro
            if fichaje.fecha.date() < hoy.date():
                fichaje.hora_salida = fichaje.fecha.replace(hour=18, minute=0) # Hora default si no hay turno
                
                # Intentar usar hora fin de turno
                if empleado.turno_id and empleado.turno_id in turnos:
                    turno = turnos[empleado.turno_id]
                    try:
                        h, m = map(int, turno.hora_fin.split(":"))
                        fichaje.hora_salida = fichaje.fecha.replace(hour=h, minute=m)
                    except:
                        pass
                
                fichaje.observaciones += " [Auto-Salida: Olvido registro]"
                fichaje.horas_trabajadas = db.calcular_horas_trabajadas(fichaje)
                db.actualizar_fichaje(fichaje)
                count += 1
                
            # Si es de HOY, verificar si ya pasó tiempo prudencial (1h después del turno)
            elif fichaje.fecha.date() == hoy.date():
                if empleado.turno_id and empleado.turno_id in turnos:
                    turno = turnos[empleado.turno_id]
                    try:
                        h, m = map(int, turno.hora_fin.split(":"))
                        hora_fin_turno = hoy.replace(hour=h, minute=m, second=0)
                        
                        # Manejar turno nocturno
                        if hora_fin_turno < fichaje.hora_entrada:
                            hora_fin_turno += timedelta(days=1)
                            
                        # Si ya pasó 1 hora del fin de turno
                        limite = hora_fin_turno + timedelta(hours=1)
                        if hoy > limite:
                             fichaje.hora_salida = hora_fin_turno
                             fichaje.observaciones += " [Auto-Salida: Turno finalizado]"
                             fichaje.horas_trabajadas = db.calcular_horas_trabajadas(fichaje)
                             db.actualizar_fichaje(fichaje)
                             count += 1
                    except:
                        pass
                        
        if count > 0:
            print(f"Auto-Checkout: {count} fichajes cerrados automáticamente")
            
    except Exception as e:
        print(f"Error en auto-checkout: {e}")

@router.get("/status/{employee_id}")
def get_employee_status(employee_id: int, db = Depends(get_db)):
    try:
        # Detectar ausencias antes de dar estado
        detect_absences(employee_id, db)
        
        hoy = datetime.now()
        fichaje = db.obtener_fichaje_del_dia(employee_id, hoy)
        
        # Verificar bloqueo
        pendientes = db.obtener_ausencias_pendientes_justificar(employee_id)
        is_blocked = False
        absence_info = None
        
        if pendientes:
             is_blocked = True
             fechas = [p.fecha for p in pendientes]
             absence_info = {
                 "start_date": min(fechas).strftime("%Y-%m-%d"),
                 "end_date": max(fechas).strftime("%Y-%m-%d"),
                 "count": len(pendientes)
             }

        status = "not_working"
        if fichaje:
            if not fichaje.hora_entrada: status = "not_working"
            elif not fichaje.hora_salida_break and not fichaje.hora_salida: status = "working"
            elif not fichaje.hora_entrada_break and not fichaje.hora_salida: status = "on_break"
            elif not fichaje.hora_salida: status = "working"
            else:
                status = "completed"
                if fichaje.tipo_fichaje == "horas_extra" and not fichaje.hora_salida:
                     status = "working_overtime"
        
        return {
            "status": status,
            "is_blocked": is_blocked,
            "absence_info": absence_info,
            "fichaje": {
                "hora_entrada": fichaje.hora_entrada.strftime("%I:%M %p") if fichaje and fichaje.hora_entrada else None,
                "hora_salida": fichaje.hora_salida.strftime("%I:%M %p") if fichaje and fichaje.hora_salida else None,
                "tipo": fichaje.tipo_fichaje if fichaje else None
            } if fichaje else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clock")
def register_clock_action(data: ClockAction, db = Depends(get_db)):
    try:
        empleado = db.obtener_empleado(data.employee_id)
        if not empleado:
            raise HTTPException(status_code=404, detail="Empleado no encontrado")

        detect_absences(data.employee_id, db)

        # Verificar ausencias pendientes (Bloqueo)
        pendientes = db.obtener_ausencias_pendientes_justificar(data.employee_id)
        if pendientes:
             # Calcular rango
             fechas = [p.fecha for p in pendientes]
             ultima_falta = max(fechas)
             primera_falta = min(fechas)
             
             # Construir detalle para el frontend
             absence_info = {
                 "start_date": primera_falta.strftime("%Y-%m-%d"),
                 "end_date": ultima_falta.strftime("%Y-%m-%d"),
                 "count": len(pendientes)
             }
             
             return JSONResponse(
                 status_code=409,
                 content={"detail": "Ausencias sin justificar", "absence_data": absence_info}
             )

        hoy = datetime.now()
        fichaje = db.obtener_fichaje_del_dia(data.employee_id, hoy)

        if data.action == "entry":
            if data.type == "horas_extra":
                config = db.obtener_configuracion()
                if not data.pin or data.pin != config.clave_aprobacion_horas_extras:
                    raise HTTPException(status_code=403, detail="PIN incorrecto")

            if not fichaje:
                nuevo_fichaje = Fichaje(empleado_id=data.employee_id, fecha=hoy, hora_entrada=hoy, tipo_fichaje=data.type)
                db.crear_fichaje(nuevo_fichaje)
                return {"message": "Entrada registrada", "time": hoy.strftime("%I:%M %p")}
            elif fichaje.hora_salida:
                 if data.type == "horas_extra":
                     # TODO: Manejar múltiples fichajes por día si se requiere
                     return {"message": "Entrada horas extra (Simulado)", "time": hoy.strftime("%I:%M %p")}
                 else:
                     raise HTTPException(status_code=400, detail="Jornada completada")
            else:
                raise HTTPException(status_code=400, detail="Ya has fichado entrada")

        elif data.action == "break_start":
            if not fichaje or not fichaje.hora_entrada or fichaje.hora_salida:
                raise HTTPException(status_code=400, detail="Acción no válida")
            fichaje.hora_salida_break = hoy
            db.actualizar_fichaje(fichaje)
            return {"message": "Inicio break", "time": hoy.strftime("%I:%M %p")}

        elif data.action == "break_end":
            if not fichaje or not fichaje.hora_salida_break:
                raise HTTPException(status_code=400, detail="No has iniciado break")
            fichaje.hora_entrada_break = hoy
            db.actualizar_fichaje(fichaje)
            return {"message": "Fin break", "time": hoy.strftime("%I:%M %p")}

        elif data.action == "exit":
            if not fichaje or not fichaje.hora_entrada:
                raise HTTPException(status_code=400, detail="No has fichado entrada")
            fichaje.hora_salida = hoy
            fichaje.horas_trabajadas = db.calcular_horas_trabajadas(fichaje)
            db.actualizar_fichaje(fichaje)
            return {"message": "Salida registrada", "time": hoy.strftime("%I:%M %p"), "hours": fichaje.horas_trabajadas}

        else:
            raise HTTPException(status_code=400, detail="Acción no válida")

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/justify")
def justify_absence(data: JustificationData, db = Depends(get_db)):
    """Justifica ausencias pendientes y permite fichar"""
    try:
        # 1. Crear registro de Ausencia
        nueva_ausencia = Ausencia(
            empleado_id=data.employee_id,
            fecha_inicio=datetime.strptime(data.fecha_inicio, "%Y-%m-%d"),
            fecha_fin=datetime.strptime(data.fecha_fin, "%Y-%m-%d"),
            tipo_ausencia=data.tipo,
            motivo_empleado=data.motivo,
            estado="justificada", # Cambiado para que aparezca en el panel de admin
            impacta_nomina="remunerado" # Default, admin decide luego
        )
        db.crear_ausencia(nueva_ausencia)

        # 2. Marcar ausencias pendientes (diarias) como justificadas (o eliminarlas/enlazarlas)
        pendientes = db.obtener_ausencias_pendientes_justificar(data.employee_id)
        for p in pendientes:
            if p.fecha >= nueva_ausencia.fecha_inicio and p.fecha <= nueva_ausencia.fecha_fin:
                db.justificar_ausencia_pendiente(p.id)
        
        # 3. Realizar fichaje de entrada automáticamente
        hoy = datetime.now()
        fichaje = db.obtener_fichaje_del_dia(data.employee_id, hoy)
        
        if not fichaje:
            nuevo_fichaje = Fichaje(
                empleado_id=data.employee_id, 
                fecha=hoy, 
                hora_entrada=hoy, 
                tipo_fichaje="normal"
            )
            db.crear_fichaje(nuevo_fichaje)
            return {"message": "Ausencia justificada y entrada registrada exitosamente", "time": hoy.strftime("%I:%M %p")}
        else:
             return {"message": "Ausencia justificada exitosamente"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/today")
def get_today_attendance(db = Depends(get_db)):
    try:
        # Ejecutar auto-checkout al consultar (lazy maintenance)
        process_auto_checkout(db)
        
        hoy = datetime.now()
        inicio_dia = hoy.replace(hour=0, minute=0, second=0)
        fin_dia = hoy.replace(hour=23, minute=59, second=59)
        
        # Obtener todos los empleados activos para detectar ausentes
        empleados_activos = db.listar_empleados(incluir_inactivos=False)
        fichajes = db.obtener_todos_fichajes_periodo(inicio_dia, fin_dia)
        
        # Map de fichajes por empleado
        fichajes_map = {f.empleado_id: (f, e) for f, e in fichajes}
        
        deptos = {d.id: d.nombre for d in db.listar_departamentos()}
        turnos = {t.id: t for t in db.listar_turnos()}
        config = db.obtener_configuracion()
        
        resultado = []
        
        for emp in empleados_activos:
            fichaje_data = fichajes_map.get(emp.id)
            
            estado = "Ausente"
            hora_entrada = None
            hora_salida = None
            fichaje_id = None
            
            if fichaje_data:
                fichaje, _ = fichaje_data
                fichaje_id = fichaje.id
                hora_entrada = fichaje.hora_entrada.strftime("%I:%M %p") if fichaje.hora_entrada else None
                hora_salida = fichaje.hora_salida.strftime("%I:%M %p") if fichaje.hora_salida else None
                
                if fichaje.hora_salida:
                    estado = "Completo"
                else:
                    # Determinar si es Tarde o A Tiempo
                    estado = "A Tiempo"
                    if fichaje.hora_entrada:
                        if emp.turno_id and emp.turno_id in turnos:
                            turno = turnos[emp.turno_id]
                            try:
                                h, m = map(int, turno.hora_inicio.split(":"))
                                # Usar la fecha del fichaje
                                expected = fichaje.hora_entrada.replace(hour=h, minute=m, second=0)
                                limit = expected + timedelta(minutes=config.tiempo_tolerancia_minutos)
                                if fichaje.hora_entrada > limit:
                                    estado = "Tarde"
                            except:
                                pass
            
            resultado.append({
                "id": fichaje_id or f"emp_{emp.id}", # ID único para key
                "empleado_id": emp.id,
                "empleado_nombre": f"{emp.nombre} {emp.apellidos}",
                "departamento": deptos.get(emp.departamento_id, emp.cargo or "-"),
                "hora_entrada": hora_entrada or "--:--",
                "hora_salida": hora_salida or "--:--",
                "estado": estado
            })
            
        return resultado
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
def get_dashboard_stats(period: str = "day", db = Depends(get_db)):
    """Obtiene estadísticas reales para el dashboard con filtros"""
    try:
        # Ejecutar mantenimiento
        process_auto_checkout(db)
        
        hoy = datetime.now()
        # print(f"DEBUG: Calculando stats para periodo: {period}. Hoy: {hoy}")
        
        # Definir rangos de fechas según filtro
        fecha_inicio_actual = hoy
        fecha_fin_actual = hoy
        fecha_inicio_anterior = hoy - timedelta(days=1)
        fecha_fin_anterior = hoy - timedelta(days=1)
        
        if period == "day":
            # Hoy vs Ayer
            fecha_inicio_actual = hoy
            fecha_fin_actual = hoy
            fecha_inicio_anterior = hoy - timedelta(days=1)
            fecha_fin_anterior = fecha_inicio_anterior
            
        elif period == "week":
            # Esta semana (Lunes-Domingo) vs Semana pasada
            start_week = hoy - timedelta(days=hoy.weekday())
            fecha_inicio_actual = start_week
            fecha_fin_actual = hoy
            
            fecha_inicio_anterior = start_week - timedelta(days=7)
            fecha_fin_anterior = fecha_inicio_anterior + timedelta(days=6)
            
        elif period == "month":
            # Este mes vs Mes pasado
            fecha_inicio_actual = hoy.replace(day=1)
            fecha_fin_actual = hoy
            
            # Mes anterior
            fecha_fin_anterior = fecha_inicio_actual - timedelta(days=1)
            fecha_inicio_anterior = fecha_fin_anterior.replace(day=1)
            
        elif period == "year":
            # Este año vs Año pasado
            fecha_inicio_actual = hoy.replace(month=1, day=1)
            fecha_fin_actual = hoy
            
            fecha_inicio_anterior = hoy.replace(year=hoy.year - 1, month=1, day=1)
            fecha_fin_anterior = hoy.replace(year=hoy.year - 1, month=12, day=31)

        # Configurar límites de tiempo para consultas DB
        ts_inicio_act = fecha_inicio_actual.replace(hour=0, minute=0, second=0)
        ts_fin_act = fecha_fin_actual.replace(hour=23, minute=59, second=59)
        
        ts_inicio_ant = fecha_inicio_anterior.replace(hour=0, minute=0, second=0)
        ts_fin_ant = fecha_fin_anterior.replace(hour=23, minute=59, second=59)

        # Obtener datos base
        empleados_activos = db.listar_empleados(incluir_inactivos=False)
        total_activos = len(empleados_activos)
        config = db.obtener_configuracion()
        turnos = {t.id: t for t in db.listar_turnos()}
        
        # Función auxiliar de cálculo
        def calcular_metricas(inicio, fin):
            # print(f"DEBUG: Calculando métricas desde {inicio} hasta {fin}")
            fichajes = db.obtener_todos_fichajes_periodo(inicio, fin)
            
            total_fichajes = len(fichajes)
            retrasos = 0
            
            # Calcular días hábiles en el periodo para estimar ausencias
            dias_totales = (fin.date() - inicio.date()).days + 1
            # Simplificación: Asumimos que todos trabajan todos los días (salvo fin de semana)
            # Para mayor precisión habría que iterar día a día y ver el turno de cada empleado
            
            # Cálculo de retrasos
            for fichaje, empleado in fichajes:
                if not fichaje.hora_entrada: continue
                
                # Determinar horario esperado
                hora_inicio_esperada = None
                if empleado.turno_id and empleado.turno_id in turnos:
                    turno = turnos[empleado.turno_id]
                    try:
                        h, m = map(int, turno.hora_inicio.split(":"))
                        # Usar la fecha del fichaje
                        hora_inicio_esperada = fichaje.hora_entrada.replace(hour=h, minute=m, second=0)
                    except:
                        hora_inicio_esperada = fichaje.hora_entrada.replace(hour=9, minute=0, second=0)
                else:
                    hora_inicio_esperada = fichaje.hora_entrada.replace(hour=9, minute=0, second=0)
                
                # Aplicar tolerancia
                limite_tolerancia = hora_inicio_esperada + timedelta(minutes=config.tiempo_tolerancia_minutos)
                
                if fichaje.hora_entrada > limite_tolerancia:
                    retrasos += 1
            
            # Cálculo de Ausencias
            # Lógica: Empleados activos * Días laborables - Fichajes únicos por día
            # (Simplificado)
            ausencias = 0
            
            # Iterar cada día del rango
            for i in range(dias_totales):
                dia_check = inicio.date() + timedelta(days=i)
                if dia_check > datetime.now().date(): break # No contar futuro
                if dia_check.weekday() >= 5: continue # Ignorar fin de semana por defecto
                
                # Fichajes de ese día
                fichajes_dia = [f for f, e in fichajes if f.fecha.date() == dia_check]
                ids_presentes = set(f.empleado_id for f in fichajes_dia)
                
                # Contar ausentes
                ausentes_dia = [e for e in empleados_activos if e.id not in ids_presentes]
                ausencias += len(ausentes_dia)

            return total_fichajes, retrasos, ausencias

        # Calcular Actual y Anterior
        fichajes_act, retrasos_act, ausencias_act = calcular_metricas(ts_inicio_act, ts_fin_act)
        fichajes_ant, retrasos_ant, ausencias_ant = calcular_metricas(ts_inicio_ant, ts_fin_ant)
        
        # Calcular variaciones porcentuales
        def calc_trend(actual, anterior):
            if anterior == 0: return "+100%" if actual > 0 else "0%"
            diff = ((actual - anterior) / anterior) * 100
            sign = "+" if diff > 0 else "-" if diff < 0 else ""
            return f"{sign}{abs(int(diff))}%"

        # Calcular porcentajes respecto al total de empleados activos
        def calc_percentage(valor, total):
            if total == 0: return 0
            return round((valor / total) * 100, 1)

        # Calcular totales esperados según período
        if period == "day":
            total_esperado = total_activos  # Por día, esperamos 1 fichaje por empleado
        elif period == "week":
            # Días laborables esta semana hasta hoy
            dias_laborables = sum(1 for i in range((fecha_fin_actual - fecha_inicio_actual).days + 1)
                                 if (fecha_inicio_actual + timedelta(days=i)).weekday() < 5
                                 and (fecha_inicio_actual + timedelta(days=i)) <= hoy)
            total_esperado = total_activos * dias_laborables
        elif period == "month":
            # Días laborables este mes hasta hoy
            dias_laborables = sum(1 for i in range((fecha_fin_actual - fecha_inicio_actual).days + 1)
                                 if (fecha_inicio_actual + timedelta(days=i)).weekday() < 5
                                 and (fecha_inicio_actual + timedelta(days=i)) <= hoy)
            total_esperado = total_activos * dias_laborables
        elif period == "year":
            # Días laborables este año hasta hoy
            dias_laborables = sum(1 for i in range((fecha_fin_actual - fecha_inicio_actual).days + 1)
                                 if (fecha_inicio_actual + timedelta(days=i)).weekday() < 5
                                 and (fecha_inicio_actual + timedelta(days=i)) <= hoy)
            total_esperado = total_activos * dias_laborables
        else:
            total_esperado = total_activos

        return {
            "activeEmployees": total_activos,
            "activeEmployeesPercentage": 100,  # Siempre 100% del total activo

            "checkinsToday": fichajes_act,
            "checkinsTrend": calc_trend(fichajes_act, fichajes_ant),
            "checkinsPercentage": calc_percentage(fichajes_act, total_esperado),

            "late": retrasos_act,
            "lateTrend": calc_trend(retrasos_act, retrasos_ant),
            "latePercentage": calc_percentage(retrasos_act, fichajes_act) if fichajes_act > 0 else 0,

            "absent": ausencias_act,
            "absentTrend": calc_trend(ausencias_act, ausencias_ant),
            "absentPercentage": calc_percentage(ausencias_act, total_esperado)
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
def get_attendance_history(
    start_date: str, 
    end_date: str,   
    employee_id: Optional[int] = None,
    db = Depends(get_db)
):
    try:
        inicio = datetime.strptime(start_date, "%Y-%m-%d").replace(hour=0, minute=0, second=0)
        fin = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
        todos = db.obtener_todos_fichajes_periodo(inicio, fin)
        
        resultados = []
        turnos = {t.id: t for t in db.listar_turnos()}
        config = db.obtener_configuracion()

        for fichaje, empleado in todos:
            if employee_id and empleado.id != employee_id: continue
            
            estado = "A Tiempo"
            if fichaje.hora_salida:
                estado = "Completo"
            else:
                # Verificar retraso
                if fichaje.hora_entrada and empleado.turno_id and empleado.turno_id in turnos:
                    turno = turnos[empleado.turno_id]
                    try:
                        h, m = map(int, turno.hora_inicio.split(":"))
                        expected = fichaje.hora_entrada.replace(hour=h, minute=m, second=0)
                        limit = expected + timedelta(minutes=config.tiempo_tolerancia_minutos)
                        if fichaje.hora_entrada > limit:
                            estado = "Tarde"
                    except:
                        pass

            resultados.append({
                "id": fichaje.id,
                "empleado_id": empleado.id,
                "empleado_nombre": f"{empleado.nombre} {empleado.apellidos}",
                "dni": empleado.dni,
                "fecha": fichaje.fecha.strftime("%Y-%m-%d"),
                "hora_entrada": fichaje.hora_entrada.strftime("%I:%M %p") if fichaje.hora_entrada else "--:--",
                "hora_salida": fichaje.hora_salida.strftime("%I:%M %p") if fichaje.hora_salida else "--:--",
                "horas_trabajadas": round(fichaje.horas_trabajadas, 2),
                "estado": estado,
                "tipo": fichaje.tipo_fichaje
            })
        return resultados
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
