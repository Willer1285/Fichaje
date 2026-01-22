"""
Gestor de base de datos SQLite
Implementa medidas de seguridad según RGPD
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from contextlib import contextmanager
import os

from app.database.models import Employee, Fichaje, HistorialModificacion, Configuracion, Turno, SolicitudVacacion, SaldoVacaciones, Ausencia, AusenciaPendiente, DispositivoEmpleado, QRActivo, Departamento, Ubicacion
from app.utils.security import hash_password


class DatabaseManager:
    """Gestión segura de la base de datos"""

    def __init__(self, db_path: str = "fichaje.db"):
        self.db_path = db_path
        self._init_database()

    def parse_datetime(self, date_str: str) -> Optional[datetime]:
        """Parsea una fecha string de la BD de forma segura"""
        if not date_str: return None
        try:
            return datetime.fromisoformat(date_str)
        except ValueError:
            try:
                # SQLite usa espacio como separador, fromisoformat espera T (pre-3.11)
                return datetime.fromisoformat(date_str.replace(" ", "T"))
            except ValueError:
                return None

    @contextmanager
    def get_connection(self):
        """Context manager para conexiones seguras"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def _init_database(self):
        """Inicializa la base de datos con las tablas necesarias"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Tabla de empleados - Cumple con RGPD (datos mínimos necesarios)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS empleados (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    apellidos TEXT NOT NULL,
                    dni TEXT UNIQUE NOT NULL,
                    telefono TEXT NOT NULL,
                    numero_empleado TEXT,
                    tipo_jornada TEXT DEFAULT 'completa',
                    es_admin BOOLEAN DEFAULT 0,
                    password_hash TEXT NOT NULL,
                    fecha_alta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    activo BOOLEAN DEFAULT 1
                )
            """)

            # Tabla de fichajes - Cumple con RD 8/2019
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fichajes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    empleado_id INTEGER NOT NULL,
                    fecha DATE NOT NULL,
                    hora_entrada TIMESTAMP,
                    hora_salida_break TIMESTAMP,
                    hora_entrada_break TIMESTAMP,
                    hora_salida TIMESTAMP,
                    horas_trabajadas REAL DEFAULT 0,
                    modificado_por INTEGER,
                    fecha_modificacion TIMESTAMP,
                    observaciones TEXT,
                    FOREIGN KEY (empleado_id) REFERENCES empleados(id),
                    FOREIGN KEY (modificado_por) REFERENCES empleados(id)
                )
            """)

            # Índices para optimizar consultas
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_fichajes_empleado
                ON fichajes(empleado_id, fecha)
            """)

            # Tabla de historial - Trazabilidad RGPD
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS historial_modificaciones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fichaje_id INTEGER NOT NULL,
                    empleado_id INTEGER NOT NULL,
                    modificado_por INTEGER NOT NULL,
                    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    campo_modificado TEXT NOT NULL,
                    valor_anterior TEXT,
                    valor_nuevo TEXT,
                    motivo TEXT,
                    FOREIGN KEY (fichaje_id) REFERENCES fichajes(id),
                    FOREIGN KEY (empleado_id) REFERENCES empleados(id),
                    FOREIGN KEY (modificado_por) REFERENCES empleados(id)
                )
            """)

            # Migración: Agregar columna es_superadmin si no existe
            cursor.execute("PRAGMA table_info(empleados)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'es_superadmin' not in columns:
                cursor.execute("ALTER TABLE empleados ADD COLUMN es_superadmin BOOLEAN DEFAULT 0")
                # Marcar al admin inicial como superadmin
                cursor.execute("UPDATE empleados SET es_superadmin = 1 WHERE dni = '00000000A'")

            # Migración: Agregar columna cargo si no existe
            cursor.execute("PRAGMA table_info(empleados)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'cargo' not in columns:
                cursor.execute("ALTER TABLE empleados ADD COLUMN cargo TEXT DEFAULT ''")

            # Migración: Agregar columna pago_por_hora si no existe
            cursor.execute("PRAGMA table_info(empleados)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'pago_por_hora' not in columns:
                cursor.execute("ALTER TABLE empleados ADD COLUMN pago_por_hora REAL DEFAULT 0.0")

            # Migración: Agregar columna pago_hora_especial si no existe
            cursor.execute("PRAGMA table_info(empleados)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'pago_hora_especial' not in columns:
                cursor.execute("ALTER TABLE empleados ADD COLUMN pago_hora_especial REAL DEFAULT 0.0")

            # Migración: Copiar datos de pago_hora_extra a pago_hora_especial si existe la columna antigua
            cursor.execute("PRAGMA table_info(empleados)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'pago_hora_extra' in columns and 'pago_hora_especial' in columns:
                # Copiar datos de la columna antigua a la nueva
                cursor.execute("UPDATE empleados SET pago_hora_especial = pago_hora_extra WHERE pago_hora_especial = 0.0 OR pago_hora_especial IS NULL")

            # Migración: Agregar columna fecha_ingreso si no existe
            cursor.execute("PRAGMA table_info(empleados)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'fecha_ingreso' not in columns:
                cursor.execute("ALTER TABLE empleados ADD COLUMN fecha_ingreso TIMESTAMP")

            # Migración: Agregar columna fecha_egreso si no existe
            cursor.execute("PRAGMA table_info(empleados)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'fecha_egreso' not in columns:
                cursor.execute("ALTER TABLE empleados ADD COLUMN fecha_egreso TIMESTAMP")

            # Migración: Agregar columna motivo_egreso si no existe
            cursor.execute("PRAGMA table_info(empleados)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'motivo_egreso' not in columns:
                cursor.execute("ALTER TABLE empleados ADD COLUMN motivo_egreso TEXT DEFAULT ''")

            # Migración: Agregar columna tipo_fichaje en fichajes si no existe
            cursor.execute("PRAGMA table_info(fichajes)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'tipo_fichaje' not in columns:
                cursor.execute("ALTER TABLE fichajes ADD COLUMN tipo_fichaje TEXT DEFAULT 'normal'")

            # Migración: Agregar columna horas_extras_aprobadas si no existe
            cursor.execute("PRAGMA table_info(fichajes)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'horas_extras_aprobadas' not in columns:
                cursor.execute("ALTER TABLE fichajes ADD COLUMN horas_extras_aprobadas REAL DEFAULT 0.0")

            # Migración: Agregar columna aprobado_por si no existe
            cursor.execute("PRAGMA table_info(fichajes)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'aprobado_por' not in columns:
                cursor.execute("ALTER TABLE fichajes ADD COLUMN aprobado_por INTEGER")

            # Tabla de configuración
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS configuracion (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    nombre_aplicacion TEXT DEFAULT 'Fichaje',
                    nombre_empresa TEXT DEFAULT '',
                    representante_legal TEXT DEFAULT '',
                    dni_cif TEXT DEFAULT '',
                    direccion TEXT DEFAULT '',
                    ciudad TEXT DEFAULT '',
                    codigo_postal TEXT DEFAULT '',
                    pais TEXT DEFAULT 'España',
                    telefono_empresa TEXT DEFAULT '',
                    logo_path TEXT DEFAULT '',
                    icono_path TEXT DEFAULT '',
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Insertar configuración por defecto si no existe
            cursor.execute("SELECT COUNT(*) FROM configuracion")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO configuracion (id, nombre_aplicacion)
                    VALUES (1, 'Fichaje')
                """)

            # Migración: Agregar columna clave_aprobacion_horas_extras si no existe
            cursor.execute("PRAGMA table_info(configuracion)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'clave_aprobacion_horas_extras' not in columns:
                cursor.execute("ALTER TABLE configuracion ADD COLUMN clave_aprobacion_horas_extras TEXT DEFAULT '123456'")

            # Migración: Agregar columnas de llegadas tarde si no existen
            cursor.execute("PRAGMA table_info(configuracion)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'permitir_llegadas_tarde' not in columns:
                cursor.execute("ALTER TABLE configuracion ADD COLUMN permitir_llegadas_tarde BOOLEAN DEFAULT 1")
            if 'tiempo_tolerancia_horas' not in columns:
                cursor.execute("ALTER TABLE configuracion ADD COLUMN tiempo_tolerancia_horas INTEGER DEFAULT 0")
            if 'tiempo_tolerancia_minutos' not in columns:
                cursor.execute("ALTER TABLE configuracion ADD COLUMN tiempo_tolerancia_minutos INTEGER DEFAULT 15")
            if 'email_empresa' not in columns:
                cursor.execute("ALTER TABLE configuracion ADD COLUMN email_empresa TEXT DEFAULT ''")

            # Migración: Agregar columna zona_horaria si no existe
            cursor.execute("PRAGMA table_info(configuracion)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'zona_horaria' not in columns:
                cursor.execute("ALTER TABLE configuracion ADD COLUMN zona_horaria TEXT DEFAULT 'Europe/Madrid'")
            
            # Migración: Agregar columna moneda si no existe
            cursor.execute("PRAGMA table_info(configuracion)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'moneda' not in columns:
                cursor.execute("ALTER TABLE configuracion ADD COLUMN moneda TEXT DEFAULT 'EUR'")

            # Tabla de turnos laborales
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS turnos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    dias_semana TEXT NOT NULL,
                    hora_inicio TEXT NOT NULL,
                    hora_fin TEXT NOT NULL,
                    activo BOOLEAN DEFAULT 1,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Índice para búsqueda rápida de turnos activos
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_turnos_activos
                ON turnos(activo)
            """)

            # Tabla de departamentos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS departamentos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    activo BOOLEAN DEFAULT 1
                )
            """)

            # Tabla de ubicaciones
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ubicaciones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    activo BOOLEAN DEFAULT 1
                )
            """)

            # Migraciones Empleados: Campos nuevos
            cursor.execute("PRAGMA table_info(empleados)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'email' not in columns:
                cursor.execute("ALTER TABLE empleados ADD COLUMN email TEXT DEFAULT ''")
            if 'foto_path' not in columns:
                cursor.execute("ALTER TABLE empleados ADD COLUMN foto_path TEXT DEFAULT ''")
            if 'departamento_id' not in columns:
                cursor.execute("ALTER TABLE empleados ADD COLUMN departamento_id INTEGER REFERENCES departamentos(id)")
            if 'ubicacion_id' not in columns:
                cursor.execute("ALTER TABLE empleados ADD COLUMN ubicacion_id INTEGER REFERENCES ubicaciones(id)")
            if 'turno_id' not in columns:
                cursor.execute("ALTER TABLE empleados ADD COLUMN turno_id INTEGER REFERENCES turnos(id)")

            # Tabla de solicitudes de vacaciones - Cumple con Art. 38 ET
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS solicitudes_vacaciones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    empleado_id INTEGER NOT NULL,
                    fecha_inicio DATE NOT NULL,
                    fecha_fin DATE NOT NULL,
                    dias_solicitados REAL NOT NULL,
                    tipo TEXT NOT NULL DEFAULT 'vacaciones_anuales',
                    subtipo TEXT DEFAULT '',
                    estado TEXT NOT NULL DEFAULT 'pendiente',
                    motivo_empleado TEXT DEFAULT '',
                    aprobado_por INTEGER,
                    motivo_rechazo TEXT DEFAULT '',
                    fecha_solicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_respuesta TIMESTAMP,
                    FOREIGN KEY (empleado_id) REFERENCES empleados(id),
                    FOREIGN KEY (aprobado_por) REFERENCES empleados(id)
                )
            """)

            # Índice para consultas de vacaciones por empleado
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_vacaciones_empleado
                ON solicitudes_vacaciones(empleado_id, estado)
            """)

            # Tabla de saldo de vacaciones por empleado y año
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS saldo_vacaciones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    empleado_id INTEGER NOT NULL,
                    anio INTEGER NOT NULL,
                    dias_totales REAL DEFAULT 30.0,
                    dias_consumidos REAL DEFAULT 0.0,
                    dias_pendientes REAL DEFAULT 30.0,
                    ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(empleado_id, anio),
                    FOREIGN KEY (empleado_id) REFERENCES empleados(id)
                )
            """)

            # Índice para consultas de saldo por empleado y año
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_saldo_empleado_anio
                ON saldo_vacaciones(empleado_id, anio)
            """)

            # Tabla de ausencias/permisos - Cumple con Art. 37 ET
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ausencias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    empleado_id INTEGER NOT NULL,
                    fecha_inicio DATE NOT NULL,
                    fecha_fin DATE NOT NULL,
                    tipo_ausencia TEXT NOT NULL DEFAULT 'ausencia_injustificada',
                    subtipo TEXT DEFAULT '',
                    estado TEXT NOT NULL DEFAULT 'pendiente_justificar',
                    es_notificacion_previa BOOLEAN DEFAULT 0,
                    motivo_empleado TEXT DEFAULT '',
                    documento_adjunto TEXT DEFAULT '',
                    aprobado_por INTEGER,
                    observaciones_admin TEXT DEFAULT '',
                    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_aprobacion TIMESTAMP,
                    impacta_nomina TEXT DEFAULT 'remunerado',
                    FOREIGN KEY (empleado_id) REFERENCES empleados(id),
                    FOREIGN KEY (aprobado_por) REFERENCES empleados(id)
                )
            """)

            # Tabla de ausencias pendientes de justificar
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ausencias_pendientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    empleado_id INTEGER NOT NULL,
                    fecha DATE NOT NULL,
                    detectada_automaticamente BOOLEAN DEFAULT 1,
                    fecha_deteccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    justificada BOOLEAN DEFAULT 0,
                    FOREIGN KEY (empleado_id) REFERENCES empleados(id)
                )
            """)

            # Índices para optimizar consultas de ausencias
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_ausencias_empleado
                ON ausencias(empleado_id, estado)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_ausencias_pendientes
                ON ausencias_pendientes(empleado_id, justificada)
            """)

            # Tabla de dispositivos autorizados por empleado
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dispositivos_empleados (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    empleado_id INTEGER NOT NULL,
                    device_fingerprint TEXT NOT NULL,
                    device_info TEXT DEFAULT '',
                    autorizado BOOLEAN DEFAULT 1,
                    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_ultimo_uso TIMESTAMP,
                    fecha_revocacion TIMESTAMP,
                    revocado_por INTEGER,
                    UNIQUE(empleado_id, device_fingerprint),
                    FOREIGN KEY (empleado_id) REFERENCES empleados(id),
                    FOREIGN KEY (revocado_por) REFERENCES empleados(id)
                )
            """)

            # Tabla de códigos QR activos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS qr_activos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo_qr TEXT UNIQUE NOT NULL,
                    fecha_generacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_expiracion TIMESTAMP NOT NULL,
                    usado BOOLEAN DEFAULT 0,
                    empleado_id INTEGER,
                    fecha_uso TIMESTAMP,
                    FOREIGN KEY (empleado_id) REFERENCES empleados(id)
                )
            """)

            # Índices para optimizar consultas de QR y dispositivos
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_dispositivos_empleado
                ON dispositivos_empleados(empleado_id, autorizado)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_qr_codigo
                ON qr_activos(codigo_qr, usado)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_qr_expiracion
                ON qr_activos(fecha_expiracion, usado)
            """)

            # Verificar y crear administrador por defecto
            cursor.execute("SELECT COUNT(*) FROM empleados WHERE dni = '00000000A'")
            if cursor.fetchone()[0] == 0:
                print("Creando usuario administrador por defecto...")
                cursor.execute("""
                    INSERT INTO empleados (
                        nombre, apellidos, dni, telefono, numero_empleado, 
                        tipo_jornada, es_admin, es_superadmin, password_hash, activo,
                        fecha_alta
                    ) VALUES (
                        'Admin', 'Sistema', '00000000A', '000000000', 'ADMIN001',
                        'completa', 1, 1, ?, 1, ?
                    )
                """, (hash_password("admin123"), datetime.now()))

            conn.commit()

    # ==================== GESTIÓN DE EMPLEADOS ====================

    def crear_empleado(self, empleado: Employee) -> int:
        """Crea un nuevo empleado"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO empleados
                (nombre, apellidos, dni, telefono, email, foto_path, numero_empleado, cargo,
                 departamento_id, ubicacion_id, turno_id, pago_por_hora, pago_hora_especial,
                 tipo_jornada, es_admin, es_superadmin, password_hash, fecha_alta, fecha_ingreso, activo,
                 fecha_egreso, motivo_egreso)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                empleado.nombre, empleado.apellidos, empleado.dni,
                empleado.telefono, empleado.email, empleado.foto_path,
                empleado.numero_empleado, empleado.cargo,
                empleado.departamento_id, empleado.ubicacion_id, empleado.turno_id,
                empleado.pago_por_hora, empleado.pago_hora_especial,
                empleado.tipo_jornada, empleado.es_admin, empleado.es_superadmin,
                empleado.password_hash, datetime.now(), empleado.fecha_ingreso, empleado.activo,
                empleado.fecha_egreso, empleado.motivo_egreso
            ))
            return cursor.lastrowid

    def obtener_empleado(self, empleado_id: int) -> Optional[Employee]:
        """Obtiene un empleado por ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM empleados WHERE id = ?", (empleado_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_employee(row)
            return None

    def obtener_empleado_por_dni(self, dni: str) -> Optional[Employee]:
        """Obtiene un empleado por DNI"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM empleados WHERE dni = ? AND activo = 1", (dni,))
            row = cursor.fetchone()
            if row:
                return self._row_to_employee(row)
            return None

    def listar_empleados(self, incluir_inactivos: bool = False) -> List[Employee]:
        """Lista todos los empleados"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if incluir_inactivos:
                cursor.execute("SELECT * FROM empleados ORDER BY apellidos, nombre")
            else:
                cursor.execute("SELECT * FROM empleados WHERE activo = 1 ORDER BY apellidos, nombre")

            return [self._row_to_employee(row) for row in cursor.fetchall()]

    def actualizar_empleado(self, empleado: Employee) -> bool:
        """Actualiza los datos de un empleado"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE empleados
                SET nombre = ?, apellidos = ?, dni = ?, telefono = ?, email = ?, foto_path = ?,
                    numero_empleado = ?, cargo = ?, departamento_id = ?, ubicacion_id = ?, turno_id = ?,
                    pago_por_hora = ?, pago_hora_especial = ?, tipo_jornada = ?,
                    es_admin = ?, es_superadmin = ?, fecha_ingreso = ?,
                    activo = ?, fecha_egreso = ?, motivo_egreso = ?
                WHERE id = ?
            """, (
                empleado.nombre, empleado.apellidos, empleado.dni,
                empleado.telefono, empleado.email, empleado.foto_path,
                empleado.numero_empleado, empleado.cargo,
                empleado.departamento_id, empleado.ubicacion_id, empleado.turno_id,
                empleado.pago_por_hora, empleado.pago_hora_especial,
                empleado.tipo_jornada, empleado.es_admin, empleado.es_superadmin,
                empleado.fecha_ingreso, empleado.activo, empleado.fecha_egreso, empleado.motivo_egreso,
                empleado.id
            ))
            return cursor.rowcount > 0

    def desactivar_empleado(self, empleado_id: int) -> bool:
        """Desactiva un empleado (baja lógica)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE empleados SET activo = 0 WHERE id = ?", (empleado_id,))
            return cursor.rowcount > 0

    def eliminar_empleado(self, empleado_id: int) -> bool:
        """Elimina permanentemente un empleado y sus fichajes"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Eliminar historial
            cursor.execute("DELETE FROM historial_modificaciones WHERE empleado_id = ?", (empleado_id,))
            # Eliminar fichajes
            cursor.execute("DELETE FROM fichajes WHERE empleado_id = ?", (empleado_id,))
            # Eliminar empleado
            cursor.execute("DELETE FROM empleados WHERE id = ?", (empleado_id,))
            return cursor.rowcount > 0

    # ==================== GESTIÓN DE FICHAJES ====================

    def crear_fichaje(self, fichaje: Fichaje) -> int:
        """Crea un nuevo fichaje"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO fichajes
                (empleado_id, fecha, hora_entrada, hora_salida_break,
                 hora_entrada_break, hora_salida, horas_trabajadas, tipo_fichaje,
                 horas_extras_aprobadas, aprobado_por, observaciones)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                fichaje.empleado_id, fichaje.fecha, fichaje.hora_entrada,
                fichaje.hora_salida_break, fichaje.hora_entrada_break,
                fichaje.hora_salida, fichaje.horas_trabajadas, fichaje.tipo_fichaje,
                fichaje.horas_extras_aprobadas, fichaje.aprobado_por, fichaje.observaciones
            ))
            return cursor.lastrowid

    def obtener_fichaje_del_dia(self, empleado_id: int, fecha: datetime) -> Optional[Fichaje]:
        """Obtiene el fichaje de un empleado para una fecha específica"""
        fecha_str = fecha.strftime("%Y-%m-%d")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM fichajes
                WHERE empleado_id = ? AND date(fecha) = date(?)
            """, (empleado_id, fecha_str))
            row = cursor.fetchone()
            if row:
                return self._row_to_fichaje(row)
            return None

    def actualizar_fichaje(self, fichaje: Fichaje, modificado_por: Optional[int] = None) -> bool:
        """Actualiza un fichaje existente"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Si hay modificación por admin, registrar en historial
            if modificado_por:
                fichaje.modificado_por = modificado_por
                fichaje.fecha_modificacion = datetime.now()

            cursor.execute("""
                UPDATE fichajes
                SET hora_entrada = ?, hora_salida_break = ?, hora_entrada_break = ?,
                    hora_salida = ?, horas_trabajadas = ?, tipo_fichaje = ?,
                    horas_extras_aprobadas = ?, aprobado_por = ?,
                    modificado_por = ?, fecha_modificacion = ?, observaciones = ?
                WHERE id = ?
            """, (
                fichaje.hora_entrada, fichaje.hora_salida_break,
                fichaje.hora_entrada_break, fichaje.hora_salida,
                fichaje.horas_trabajadas, fichaje.tipo_fichaje,
                fichaje.horas_extras_aprobadas, fichaje.aprobado_por,
                fichaje.modificado_por, fichaje.fecha_modificacion, fichaje.observaciones, fichaje.id
            ))
            return cursor.rowcount > 0

    def obtener_ultimo_fichaje(self, empleado_id: int) -> Optional[Fichaje]:
        """Obtiene el último fichaje realizado por el empleado"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM fichajes
                WHERE empleado_id = ?
                ORDER BY fecha DESC, hora_entrada DESC
                LIMIT 1
            """, (empleado_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_fichaje(row)
            return None

    def obtener_fichajes_periodo(self, empleado_id: int, fecha_inicio: datetime,
                                  fecha_fin: datetime) -> List[Fichaje]:
        """Obtiene los fichajes de un periodo"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM fichajes
                WHERE empleado_id = ? AND fecha BETWEEN ? AND ?
                ORDER BY fecha DESC
            """, (empleado_id, fecha_inicio, fecha_fin))
            return [self._row_to_fichaje(row) for row in cursor.fetchall()]

    def obtener_todos_fichajes_periodo(self, fecha_inicio: datetime,
                                        fecha_fin: datetime) -> List[Tuple[Fichaje, Employee]]:
        """Obtiene todos los fichajes de un periodo con datos del empleado"""
        # print(f"DEBUG: Consultando fichajes entre {fecha_inicio} y {fecha_fin}")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Asegurar conversión a string si es necesario para SQLite (a veces ayuda con formatos mixtos)
            # Pero probemos primero con los objetos directos y loggeando el count
            
            cursor.execute("""
                SELECT f.*, e.nombre, e.apellidos, e.numero_empleado, e.tipo_jornada, e.turno_id, e.departamento_id
                FROM fichajes f
                JOIN empleados e ON f.empleado_id = e.id
                WHERE f.fecha >= ? AND f.fecha <= ?
                ORDER BY f.fecha DESC, e.apellidos, e.nombre
            """, (fecha_inicio, fecha_fin))
            
            rows = cursor.fetchall()
            # print(f"DEBUG: Fichajes encontrados: {len(rows)}")

            resultados = []
            for row in rows:
                fichaje = self._row_to_fichaje(row)
                # Usar get_field safe approach si es posible o try/except, pero aquí sabemos que columns existen
                try:
                    turno_id = row['turno_id']
                except:
                    turno_id = None
                
                try:
                    dept_id = row['departamento_id']
                except:
                    dept_id = None

                empleado = Employee(
                    id=fichaje.empleado_id,
                    nombre=row['nombre'],
                    apellidos=row['apellidos'],
                    numero_empleado=row['numero_empleado'],
                    tipo_jornada=row['tipo_jornada'],
                    turno_id=turno_id,
                    departamento_id=dept_id
                )
                resultados.append((fichaje, empleado))
            return resultados

    # ==================== CÁLCULOS DE HORAS ====================

    def calcular_horas_trabajadas(self, fichaje: Fichaje) -> float:
        """Calcula las horas trabajadas en un fichaje respetando turnos y tolerancias"""
        if not fichaje.hora_entrada or not fichaje.hora_salida:
            return 0.0

        # Para horas extras, calcular sin restricciones de turno
        if fichaje.tipo_fichaje == "horas_extra":
            total = fichaje.hora_salida - fichaje.hora_entrada
            if fichaje.hora_salida_break and fichaje.hora_entrada_break:
                break_time = fichaje.hora_entrada_break - fichaje.hora_salida_break
                total -= break_time
            return round(total.total_seconds() / 3600, 2)

        # Obtener empleado y su turno
        empleado = self.obtener_empleado(fichaje.empleado_id)
        if not empleado:
            # Cálculo estándar si no se encuentra el empleado
            total = fichaje.hora_salida - fichaje.hora_entrada
            if fichaje.hora_salida_break and fichaje.hora_entrada_break:
                break_time = fichaje.hora_entrada_break - fichaje.hora_salida_break
                total -= break_time
            return round(total.total_seconds() / 3600, 2)

        # Buscar turno por nombre
        turnos = self.listar_turnos(solo_activos=False)
        turno = next((t for t in turnos if t.nombre == empleado.tipo_jornada), None)

        if not turno:
            # Si no hay turno configurado, calcular normal
            total = fichaje.hora_salida - fichaje.hora_entrada
            if fichaje.hora_salida_break and fichaje.hora_entrada_break:
                break_time = fichaje.hora_entrada_break - fichaje.hora_salida_break
                total -= break_time
            return round(total.total_seconds() / 3600, 2)

        # Obtener configuración de llegadas tarde
        config = self.obtener_configuracion()

        # Parsear horarios del turno
        h_turno_ini, m_turno_ini = map(int, turno.hora_inicio.split(":"))
        h_turno_fin, m_turno_fin = map(int, turno.hora_fin.split(":"))

        # Crear datetimes para comparar (usando la fecha del fichaje)
        fecha_base = fichaje.fecha.date()
        turno_inicio = datetime.combine(fecha_base, datetime.min.time()).replace(
            hour=h_turno_ini, minute=m_turno_ini
        )
        turno_fin = datetime.combine(fecha_base, datetime.min.time()).replace(
            hour=h_turno_fin, minute=m_turno_fin
        )

        # Manejar turnos que cruzan medianoche
        if turno_fin <= turno_inicio:
            turno_fin += timedelta(days=1)

        # Ajustar hora de entrada según turno
        hora_entrada_efectiva = fichaje.hora_entrada

        # Si llegó antes del turno, contar desde inicio del turno
        if fichaje.hora_entrada < turno_inicio:
            hora_entrada_efectiva = turno_inicio

        # Si llegó tarde, verificar tolerancia
        if fichaje.hora_entrada > turno_inicio and config.permitir_llegadas_tarde:
            tolerancia = timedelta(
                hours=config.tiempo_tolerancia_horas,
                minutes=config.tiempo_tolerancia_minutos
            )
            llegada_permitida = turno_inicio + tolerancia

            # Si llegó dentro de la tolerancia, contar desde inicio del turno
            if fichaje.hora_entrada <= llegada_permitida:
                hora_entrada_efectiva = turno_inicio
            # Si llegó después de la tolerancia, contar desde cuando llegó (descuento automático)
            # hora_entrada_efectiva ya es fichaje.hora_entrada

        # Ajustar hora de salida según turno
        hora_salida_efectiva = fichaje.hora_salida

        # Si salió después del turno, contar solo hasta el fin del turno
        if fichaje.hora_salida > turno_fin:
            hora_salida_efectiva = turno_fin

        # Calcular horas totales dentro del turno
        total = hora_salida_efectiva - hora_entrada_efectiva

        # Restar tiempo de break si existe
        if fichaje.hora_salida_break and fichaje.hora_entrada_break:
            break_time = fichaje.hora_entrada_break - fichaje.hora_salida_break
            total -= break_time

        # Asegurar que no sea negativo
        if total.total_seconds() < 0:
            return 0.0

        return round(total.total_seconds() / 3600, 2)

    def obtener_resumen_mensual(self, empleado_id: int, mes: int, anio: int) -> dict:
        """Obtiene resumen de horas del mes"""
        fecha_inicio = datetime(anio, mes, 1)
        if mes == 12:
            fecha_fin = datetime(anio + 1, 1, 1) - timedelta(days=1)
        else:
            fecha_fin = datetime(anio, mes + 1, 1) - timedelta(days=1)

        fichajes = self.obtener_fichajes_periodo(empleado_id, fecha_inicio, fecha_fin)

        total_horas = sum(f.horas_trabajadas for f in fichajes)
        dias_trabajados = len(fichajes)

        return {
            'total_horas': round(total_horas, 2),
            'dias_trabajados': dias_trabajados,
            'promedio_diario': round(total_horas / dias_trabajados, 2) if dias_trabajados > 0 else 0
        }

    # ==================== HISTORIAL Y TRAZABILIDAD ====================

    def registrar_modificacion(self, historial: HistorialModificacion) -> int:
        """Registra una modificación en el historial"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO historial_modificaciones
                (fichaje_id, empleado_id, modificado_por, campo_modificado,
                 valor_anterior, valor_nuevo, motivo)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                historial.fichaje_id, historial.empleado_id, historial.modificado_por,
                historial.campo_modificado, historial.valor_anterior,
                historial.valor_nuevo, historial.motivo
            ))
            return cursor.lastrowid

    def obtener_modificaciones_recientes(self, fecha: datetime) -> List[dict]:
        """Obtiene modificaciones realizadas en una fecha específica"""
        fecha_str = fecha.strftime("%Y-%m-%d")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT h.*, e.nombre, e.apellidos 
                FROM historial_modificaciones h
                JOIN empleados e ON h.empleado_id = e.id
                WHERE date(h.fecha_modificacion) = date(?)
            """, (fecha_str,))
            
            resultados = []
            for row in cursor.fetchall():
                resultados.append(dict(row))
            return resultados

    # ==================== UTILIDADES ====================

    def _row_to_employee(self, row) -> Employee:
        """Convierte una fila de BD a objeto Employee"""
        # Helper para extraer campos con manejo de errores
        def get_field(field, default=None):
            try:
                return row[field] if row[field] is not None else default
            except (KeyError, IndexError):
                return default

        return Employee(
            id=row['id'],
            nombre=row['nombre'],
            apellidos=row['apellidos'],
            dni=row['dni'],
            telefono=row['telefono'],
            email=get_field('email', ""),
            foto_path=get_field('foto_path', ""),
            numero_empleado=row['numero_empleado'],
            cargo=get_field('cargo', ""),
            departamento_id=get_field('departamento_id'),
            ubicacion_id=get_field('ubicacion_id'),
            turno_id=get_field('turno_id'),
            pago_por_hora=float(get_field('pago_por_hora', 0.0)),
            pago_hora_especial=float(get_field('pago_hora_especial', 0.0)),
            tipo_jornada=row['tipo_jornada'],
            es_admin=bool(row['es_admin']),
            es_superadmin=bool(get_field('es_superadmin', False)),
            password_hash=row['password_hash'],
            fecha_alta=self.parse_datetime(get_field('fecha_alta')),
            fecha_ingreso=self.parse_datetime(get_field('fecha_ingreso')),
            activo=bool(row['activo']),
            fecha_egreso=self.parse_datetime(get_field('fecha_egreso')),
            motivo_egreso=get_field('motivo_egreso', "")
        )

    def _row_to_fichaje(self, row) -> Fichaje:
        """Convierte una fila de BD a objeto Fichaje"""
        # Manejar tipo_fichaje que puede no existir en BD antiguas
        try:
            tipo_fichaje = row['tipo_fichaje'] or "normal"
        except (KeyError, IndexError):
            tipo_fichaje = "normal"

        # Manejar horas_extras_aprobadas que puede no existir en BD antiguas
        try:
            horas_extras_aprobadas = float(row['horas_extras_aprobadas']) if row['horas_extras_aprobadas'] else 0.0
        except (KeyError, IndexError, ValueError):
            horas_extras_aprobadas = 0.0

        # Manejar aprobado_por que puede no existir en BD antiguas
        try:
            aprobado_por = row['aprobado_por']
        except (KeyError, IndexError):
            aprobado_por = None

        return Fichaje(
            id=row['id'],
            empleado_id=row['empleado_id'],
            fecha=self.parse_datetime(row['fecha']),
            hora_entrada=self.parse_datetime(row['hora_entrada']),
            hora_salida_break=self.parse_datetime(row['hora_salida_break']),
            hora_entrada_break=self.parse_datetime(row['hora_entrada_break']),
            hora_salida=self.parse_datetime(row['hora_salida']),
            horas_trabajadas=row['horas_trabajadas'],
            tipo_fichaje=tipo_fichaje,
            horas_extras_aprobadas=horas_extras_aprobadas,
            aprobado_por=aprobado_por,
            modificado_por=row['modificado_por'],
            fecha_modificacion=self.parse_datetime(row['fecha_modificacion']),
            observaciones=row['observaciones'] or ""
        )

    # ==================== GESTIÓN DE CONFIGURACIÓN ====================

    def obtener_configuracion(self) -> Configuracion:
        """Obtiene la configuración de la aplicación"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM configuracion WHERE id = 1")
            row = cursor.fetchone()
            if row:
                # Manejar clave_aprobacion_horas_extras que puede no existir en BD antiguas
                try:
                    clave_aprobacion = row['clave_aprobacion_horas_extras'] or "123456"
                except (KeyError, IndexError):
                    clave_aprobacion = "123456"

                # Manejar campos de llegadas tarde que pueden no existir en BD antiguas
                try:
                    permitir_llegadas_tarde = bool(row['permitir_llegadas_tarde'])
                except (KeyError, IndexError):
                    permitir_llegadas_tarde = True

                try:
                    tiempo_tolerancia_horas = int(row['tiempo_tolerancia_horas']) if row['tiempo_tolerancia_horas'] else 0
                except (KeyError, IndexError, ValueError):
                    tiempo_tolerancia_horas = 0

                try:
                    tiempo_tolerancia_minutos = int(row['tiempo_tolerancia_minutos']) if row['tiempo_tolerancia_minutos'] else 15
                except (KeyError, IndexError, ValueError):
                    tiempo_tolerancia_minutos = 15

                try:
                    email_empresa = row['email_empresa'] or ""
                except (KeyError, IndexError):
                    email_empresa = ""
                
                try:
                    zona_horaria = row['zona_horaria'] or "Europe/Madrid"
                except (KeyError, IndexError):
                    zona_horaria = "Europe/Madrid"
                
                try:
                    moneda = row['moneda'] or "EUR"
                except (KeyError, IndexError):
                    moneda = "EUR"

                return Configuracion(
                    id=row['id'],
                    nombre_aplicacion=row['nombre_aplicacion'],
                    nombre_empresa=row['nombre_empresa'] or "",
                    representante_legal=row['representante_legal'] or "",
                    dni_cif=row['dni_cif'] or "",
                    direccion=row['direccion'] or "",
                    ciudad=row['ciudad'] or "",
                    codigo_postal=row['codigo_postal'] or "",
                    pais=row['pais'] or "España",
                    telefono_empresa=row['telefono_empresa'] or "",
                    email_empresa=email_empresa,
                    logo_path=row['logo_path'] or "",
                    icono_path=row['icono_path'] or "",
                    clave_aprobacion_horas_extras=clave_aprobacion,
                    permitir_llegadas_tarde=permitir_llegadas_tarde,
                    tiempo_tolerancia_horas=tiempo_tolerancia_horas,
                    tiempo_tolerancia_minutos=tiempo_tolerancia_minutos,
                    zona_horaria=zona_horaria,
                    moneda=moneda,
                    fecha_actualizacion=datetime.fromisoformat(row['fecha_actualizacion']) if row['fecha_actualizacion'] else None
                )
            else:
                # Retornar configuración por defecto
                return Configuracion()

    def actualizar_configuracion(self, config: Configuracion) -> bool:
        """Actualiza la configuración de la aplicación"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE configuracion
                SET nombre_aplicacion = ?,
                    nombre_empresa = ?,
                    representante_legal = ?,
                    dni_cif = ?,
                    direccion = ?,
                    ciudad = ?,
                    codigo_postal = ?,
                    pais = ?,
                    telefono_empresa = ?,
                    email_empresa = ?,
                    logo_path = ?,
                    icono_path = ?,
                    clave_aprobacion_horas_extras = ?,
                    permitir_llegadas_tarde = ?,
                    tiempo_tolerancia_horas = ?,
                    tiempo_tolerancia_minutos = ?,
                    zona_horaria = ?,
                    moneda = ?,
                    fecha_actualizacion = ?
                WHERE id = 1
            """, (
                config.nombre_aplicacion,
                config.nombre_empresa,
                config.representante_legal,
                config.dni_cif,
                config.direccion,
                config.ciudad,
                config.codigo_postal,
                config.pais,
                config.telefono_empresa,
                config.email_empresa,
                config.logo_path,
                config.icono_path,
                config.clave_aprobacion_horas_extras,
                config.permitir_llegadas_tarde,
                config.tiempo_tolerancia_horas,
                config.tiempo_tolerancia_minutos,
                config.zona_horaria,
                config.moneda,
                datetime.now()
            ))
            return cursor.rowcount > 0

    # ==================== GESTIÓN DE TURNOS ====================

    def crear_turno(self, turno: Turno) -> int:
        """Crea un nuevo turno laboral"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO turnos
                (nombre, dias_semana, hora_inicio, hora_fin, activo, fecha_creacion)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                turno.nombre, turno.dias_semana, turno.hora_inicio,
                turno.hora_fin, turno.activo, datetime.now()
            ))
            return cursor.lastrowid

    def obtener_turno(self, turno_id: int) -> Optional[Turno]:
        """Obtiene un turno por ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM turnos WHERE id = ?", (turno_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_turno(row)
            return None

    def listar_turnos(self, solo_activos: bool = True) -> List[Turno]:
        """Lista todos los turnos"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if solo_activos:
                cursor.execute("SELECT * FROM turnos WHERE activo = 1 ORDER BY nombre")
            else:
                cursor.execute("SELECT * FROM turnos ORDER BY nombre")
            return [self._row_to_turno(row) for row in cursor.fetchall()]

    def actualizar_turno(self, turno: Turno) -> bool:
        """Actualiza un turno existente"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE turnos
                SET nombre = ?, dias_semana = ?, hora_inicio = ?,
                    hora_fin = ?, activo = ?
                WHERE id = ?
            """, (
                turno.nombre, turno.dias_semana, turno.hora_inicio,
                turno.hora_fin, turno.activo, turno.id
            ))
            return cursor.rowcount > 0

    def eliminar_turno(self, turno_id: int) -> bool:
        """Desactiva un turno (no lo elimina físicamente)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE turnos SET activo = 0 WHERE id = ?", (turno_id,))
            return cursor.rowcount > 0

    def _row_to_turno(self, row) -> Turno:
        """Convierte una fila de BD a objeto Turno"""
        return Turno(
            id=row['id'],
            nombre=row['nombre'],
            dias_semana=row['dias_semana'],
            hora_inicio=row['hora_inicio'],
            hora_fin=row['hora_fin'],
            activo=bool(row['activo']),
            fecha_creacion=datetime.fromisoformat(row['fecha_creacion']) if row['fecha_creacion'] else None
        )

    def contar_empleados_por_turno(self, nombre_turno: str) -> int:
        """Cuenta cuántos empleados están asignados a un turno"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM empleados WHERE tipo_jornada = ? AND activo = 1", (nombre_turno,))
            return cursor.fetchone()[0]

    def obtener_empleados_por_turno(self, nombre_turno: str) -> List[Employee]:
        """Obtiene la lista de empleados asignados a un turno"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM empleados WHERE tipo_jornada = ? AND activo = 1", (nombre_turno,))
            return [self._row_to_employee(row) for row in cursor.fetchall()]

    def migrar_empleados_a_turno(self, turno_origen: str, turno_destino: str) -> int:
        """Migra todos los empleados de un turno a otro"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE empleados
                SET tipo_jornada = ?
                WHERE tipo_jornada = ? AND activo = 1
            """, (turno_destino, turno_origen))
            return cursor.rowcount

    def calcular_horas_extras_dia(self, empleado_id: int, fecha: datetime) -> float:
        """Calcula el total de horas extras aprobadas del empleado en un día específico"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            fecha_inicio = fecha.replace(hour=0, minute=0, second=0, microsecond=0)
            fecha_fin = fecha.replace(hour=23, minute=59, second=59, microsecond=999999)

            cursor.execute("""
                SELECT COALESCE(SUM(horas_extras_aprobadas), 0)
                FROM fichajes
                WHERE empleado_id = ?
                AND tipo_fichaje = 'horas_extra'
                AND fecha >= ? AND fecha <= ?
            """, (empleado_id, fecha_inicio, fecha_fin))

            return cursor.fetchone()[0]

    def calcular_horas_extras_anio(self, empleado_id: int, anio: int) -> float:
        """Calcula el total de horas extras aprobadas del empleado en un año"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            fecha_inicio = datetime(anio, 1, 1, 0, 0, 0)
            fecha_fin = datetime(anio, 12, 31, 23, 59, 59)

            cursor.execute("""
                SELECT COALESCE(SUM(horas_extras_aprobadas), 0)
                FROM fichajes
                WHERE empleado_id = ?
                AND tipo_fichaje = 'horas_extra'
                AND fecha >= ? AND fecha <= ?
            """, (empleado_id, fecha_inicio, fecha_fin))

            return cursor.fetchone()[0]

    # ==================== GESTIÓN DE VACACIONES ====================

    def crear_solicitud_vacacion(self, solicitud: SolicitudVacacion) -> int:
        """Crea una nueva solicitud de vacaciones"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO solicitudes_vacaciones (
                    empleado_id, fecha_inicio, fecha_fin, dias_solicitados,
                    tipo, subtipo, estado, motivo_empleado, fecha_solicitud
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                solicitud.empleado_id,
                solicitud.fecha_inicio,
                solicitud.fecha_fin,
                solicitud.dias_solicitados,
                solicitud.tipo,
                solicitud.subtipo,
                solicitud.estado,
                solicitud.motivo_empleado,
                solicitud.fecha_solicitud or datetime.now()
            ))
            return cursor.lastrowid

    def obtener_solicitudes_empleado(self, empleado_id: int, incluir_historial: bool = False) -> List[SolicitudVacacion]:
        """Obtiene las solicitudes de vacaciones de un empleado"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if incluir_historial:
                cursor.execute("""
                    SELECT * FROM solicitudes_vacaciones
                    WHERE empleado_id = ?
                    ORDER BY fecha_solicitud DESC
                """, (empleado_id,))
            else:
                cursor.execute("""
                    SELECT * FROM solicitudes_vacaciones
                    WHERE empleado_id = ? AND estado = 'pendiente'
                    ORDER BY fecha_solicitud DESC
                """, (empleado_id,))

            return [self._row_to_solicitud_vacacion(row) for row in cursor.fetchall()]

    def obtener_solicitud_por_id(self, solicitud_id: int) -> Optional[SolicitudVacacion]:
        """Obtiene una solicitud de vacaciones por su ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM solicitudes_vacaciones WHERE id = ?
            """, (solicitud_id,))
            row = cursor.fetchone()
            return self._row_to_solicitud_vacacion(row) if row else None

    def obtener_solicitudes_pendientes(self) -> List[Tuple[SolicitudVacacion, Employee]]:
        """Obtiene todas las solicitudes pendientes con datos del empleado"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    sv.id as solicitud_id,
                    sv.empleado_id as solicitud_empleado_id,
                    sv.fecha_inicio,
                    sv.fecha_fin,
                    sv.dias_solicitados,
                    sv.tipo,
                    sv.subtipo,
                    sv.estado,
                    sv.motivo_empleado,
                    sv.aprobado_por,
                    sv.motivo_rechazo,
                    sv.fecha_solicitud,
                    sv.fecha_respuesta,
                    e.id as id,
                    e.nombre,
                    e.apellidos,
                    e.dni,
                    e.telefono,
                    e.numero_empleado,
                    e.cargo,
                    e.pago_por_hora,
                    e.pago_hora_especial,
                    e.tipo_jornada,
                    e.fecha_alta,
                    e.fecha_ingreso,
                    e.fecha_egreso,
                    e.motivo_egreso,
                    e.activo,
                    e.es_admin,
                    e.es_superadmin,
                    e.password_hash
                FROM solicitudes_vacaciones sv
                INNER JOIN empleados e ON sv.empleado_id = e.id
                WHERE sv.estado = 'pendiente'
                ORDER BY sv.fecha_solicitud ASC
            """)

            resultados = []
            for row in cursor.fetchall():
                # Construir datos de solicitud con aliases
                row_dict = dict(row)
                solicitud_data = {
                    'id': row_dict['solicitud_id'],
                    'empleado_id': row_dict['solicitud_empleado_id'],
                    'fecha_inicio': row_dict['fecha_inicio'],
                    'fecha_fin': row_dict['fecha_fin'],
                    'dias_solicitados': row_dict['dias_solicitados'],
                    'tipo': row_dict['tipo'],
                    'subtipo': row_dict['subtipo'],
                    'estado': row_dict['estado'],
                    'motivo_empleado': row_dict['motivo_empleado'],
                    'aprobado_por': row_dict['aprobado_por'],
                    'motivo_rechazo': row_dict['motivo_rechazo'],
                    'fecha_solicitud': row_dict['fecha_solicitud'],
                    'fecha_respuesta': row_dict['fecha_respuesta']
                }

                # Construir datos de empleado (ya tiene el alias correcto para 'id')
                empleado_data = {
                    'id': row_dict['id'],
                    'nombre': row_dict['nombre'],
                    'apellidos': row_dict['apellidos'],
                    'dni': row_dict['dni'],
                    'telefono': row_dict['telefono'],
                    'numero_empleado': row_dict['numero_empleado'],
                    'cargo': row_dict.get('cargo'),
                    'pago_por_hora': row_dict.get('pago_por_hora'),
                    'pago_hora_especial': row_dict.get('pago_hora_especial'),
                    'tipo_jornada': row_dict['tipo_jornada'],
                    'fecha_alta': row_dict.get('fecha_alta'),
                    'fecha_ingreso': row_dict.get('fecha_ingreso'),
                    'fecha_egreso': row_dict.get('fecha_egreso'),
                    'motivo_egreso': row_dict.get('motivo_egreso'),
                    'activo': row_dict['activo'],
                    'es_admin': row_dict['es_admin'],
                    'es_superadmin': row_dict.get('es_superadmin'),
                    'password_hash': row_dict['password_hash']
                }

                solicitud = self._row_to_solicitud_vacacion(solicitud_data)
                empleado = self._row_to_employee(empleado_data)
                resultados.append((solicitud, empleado))

            return resultados

    def aprobar_solicitud_vacacion(self, solicitud_id: int, admin_id: int) -> bool:
        """Aprueba una solicitud de vacaciones y actualiza el saldo"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Obtener la solicitud
            cursor.execute("SELECT * FROM solicitudes_vacaciones WHERE id = ?", (solicitud_id,))
            row = cursor.fetchone()
            if not row:
                return False

            solicitud = self._row_to_solicitud_vacacion(row)

            # Actualizar estado de la solicitud
            cursor.execute("""
                UPDATE solicitudes_vacaciones
                SET estado = 'aprobada', aprobado_por = ?, fecha_respuesta = ?
                WHERE id = ?
            """, (admin_id, datetime.now(), solicitud_id))

            # Actualizar saldo de vacaciones
            anio = solicitud.fecha_inicio.year
            self._actualizar_saldo_vacaciones(cursor, solicitud.empleado_id, anio, solicitud.dias_solicitados)

            return True

    def rechazar_solicitud_vacacion(self, solicitud_id: int, admin_id: int, motivo: str) -> bool:
        """Rechaza una solicitud de vacaciones"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE solicitudes_vacaciones
                SET estado = 'rechazada', aprobado_por = ?, motivo_rechazo = ?, fecha_respuesta = ?
                WHERE id = ?
            """, (admin_id, motivo, datetime.now(), solicitud_id))

            return cursor.rowcount > 0

    def obtener_saldo_vacaciones(self, empleado_id: int, anio: int) -> SaldoVacaciones:
        """Obtiene el saldo de vacaciones de un empleado para un año"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM saldo_vacaciones
                WHERE empleado_id = ? AND anio = ?
            """, (empleado_id, anio))

            row = cursor.fetchone()
            if row:
                return self._row_to_saldo_vacaciones(row)
            else:
                # Si no existe, inicializar saldo para ese año
                return self.inicializar_saldo_vacaciones(empleado_id, anio)

    def inicializar_saldo_vacaciones(self, empleado_id: int, anio: int) -> SaldoVacaciones:
        """Inicializa el saldo de vacaciones para un empleado en un año"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Obtener empleado para calcular días proporcionales si ingresó en mitad del año
            empleado = self.obtener_empleado(empleado_id)
            dias_totales = 30.0  # Por defecto según normativa española

            if empleado and empleado.fecha_ingreso:
                fecha_ingreso = empleado.fecha_ingreso
                if fecha_ingreso.year == anio and fecha_ingreso.month > 1:
                    # Calcular días proporcionales
                    meses_trabajados = 13 - fecha_ingreso.month  # Meses completos + el actual
                    dias_totales = round((30.0 / 12) * meses_trabajados, 2)

            cursor.execute("""
                INSERT INTO saldo_vacaciones (empleado_id, anio, dias_totales, dias_consumidos, dias_pendientes)
                VALUES (?, ?, ?, 0.0, ?)
            """, (empleado_id, anio, dias_totales, dias_totales))

            return SaldoVacaciones(
                id=cursor.lastrowid,
                empleado_id=empleado_id,
                anio=anio,
                dias_totales=dias_totales,
                dias_consumidos=0.0,
                dias_pendientes=dias_totales,
                ultima_actualizacion=datetime.now()
            )

    def _actualizar_saldo_vacaciones(self, cursor, empleado_id: int, anio: int, dias_consumidos: float):
        """Actualiza el saldo de vacaciones (método interno)"""
        # Verificar si existe el saldo
        cursor.execute("""
            SELECT id, dias_consumidos FROM saldo_vacaciones
            WHERE empleado_id = ? AND anio = ?
        """, (empleado_id, anio))

        row = cursor.fetchone()
        if row:
            # Actualizar consumidos
            nuevos_consumidos = row['dias_consumidos'] + dias_consumidos
            cursor.execute("""
                UPDATE saldo_vacaciones
                SET dias_consumidos = ?,
                    dias_pendientes = dias_totales - ?,
                    ultima_actualizacion = ?
                WHERE id = ?
            """, (nuevos_consumidos, nuevos_consumidos, datetime.now(), row['id']))
        else:
            # Crear nuevo saldo si no existe
            saldo = self.inicializar_saldo_vacaciones(empleado_id, anio)
            cursor.execute("""
                UPDATE saldo_vacaciones
                SET dias_consumidos = ?,
                    dias_pendientes = dias_totales - ?
                WHERE id = ?
            """, (dias_consumidos, dias_consumidos, saldo.id))

    def calcular_dias_laborables(self, fecha_inicio: datetime, fecha_fin: datetime) -> float:
        """Calcula los días laborables entre dos fechas (excluyendo sábados y domingos)"""
        dias = 0
        fecha_actual = fecha_inicio

        while fecha_actual <= fecha_fin:
            # 0 = Lunes, 6 = Domingo
            if fecha_actual.weekday() < 5:  # Lunes a Viernes
                dias += 1
            fecha_actual += timedelta(days=1)

        return float(dias)

    def _row_to_solicitud_vacacion(self, row) -> SolicitudVacacion:
        """Convierte una fila de DB a objeto SolicitudVacacion"""
        return SolicitudVacacion(
            id=row['id'],
            empleado_id=row['empleado_id'],
            fecha_inicio=datetime.fromisoformat(row['fecha_inicio']) if row['fecha_inicio'] else None,
            fecha_fin=datetime.fromisoformat(row['fecha_fin']) if row['fecha_fin'] else None,
            dias_solicitados=row['dias_solicitados'],
            tipo=row['tipo'],
            subtipo=row['subtipo'],
            estado=row['estado'],
            motivo_empleado=row['motivo_empleado'],
            aprobado_por=row['aprobado_por'],
            motivo_rechazo=row['motivo_rechazo'],
            fecha_solicitud=datetime.fromisoformat(row['fecha_solicitud']) if row['fecha_solicitud'] else None,
            fecha_respuesta=datetime.fromisoformat(row['fecha_respuesta']) if row['fecha_respuesta'] else None
        )

    def _row_to_saldo_vacaciones(self, row) -> SaldoVacaciones:
        """Convierte una fila de DB a objeto SaldoVacaciones"""
        return SaldoVacaciones(
            id=row['id'],
            empleado_id=row['empleado_id'],
            anio=row['anio'],
            dias_totales=row['dias_totales'],
            dias_consumidos=row['dias_consumidos'],
            dias_pendientes=row['dias_pendientes'],
            ultima_actualizacion=datetime.fromisoformat(row['ultima_actualizacion']) if row['ultima_actualizacion'] else None
        )

    # ==================== GESTIÓN DE AUSENCIAS ====================

    def crear_ausencia(self, ausencia: Ausencia) -> int:
        """Crea una nueva ausencia/permiso"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO ausencias (
                    empleado_id, fecha_inicio, fecha_fin, tipo_ausencia, subtipo,
                    estado, es_notificacion_previa, motivo_empleado, documento_adjunto,
                    impacta_nomina, fecha_registro
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ausencia.empleado_id,
                ausencia.fecha_inicio,
                ausencia.fecha_fin,
                ausencia.tipo_ausencia,
                ausencia.subtipo,
                ausencia.estado,
                ausencia.es_notificacion_previa,
                ausencia.motivo_empleado,
                ausencia.documento_adjunto,
                ausencia.impacta_nomina,
                ausencia.fecha_registro or datetime.now()
            ))
            return cursor.lastrowid

    def obtener_ausencias_empleado(self, empleado_id: int, incluir_historial: bool = False) -> List[Ausencia]:
        """Obtiene las ausencias de un empleado"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if incluir_historial:
                cursor.execute("""
                    SELECT * FROM ausencias
                    WHERE empleado_id = ?
                    ORDER BY fecha_registro DESC
                """, (empleado_id,))
            else:
                cursor.execute("""
                    SELECT * FROM ausencias
                    WHERE empleado_id = ? AND estado IN ('pendiente_justificar', 'justificada', 'notificada')
                    ORDER BY fecha_registro DESC
                """, (empleado_id,))

            return [self._row_to_ausencia(row) for row in cursor.fetchall()]

    def obtener_ausencia_por_id(self, ausencia_id: int) -> Optional[Ausencia]:
        """Obtiene una ausencia por su ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM ausencias WHERE id = ?
            """, (ausencia_id,))
            row = cursor.fetchone()
            return self._row_to_ausencia(row) if row else None

    def obtener_ausencias_pendientes_admin(self) -> List[Tuple[Ausencia, Employee]]:
        """Obtiene todas las ausencias pendientes de aprobación con datos del empleado"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    a.id as ausencia_id,
                    a.empleado_id as ausencia_empleado_id,
                    a.fecha_inicio,
                    a.fecha_fin,
                    a.tipo_ausencia,
                    a.subtipo,
                    a.estado,
                    a.es_notificacion_previa,
                    a.motivo_empleado,
                    a.documento_adjunto,
                    a.aprobado_por,
                    a.observaciones_admin,
                    a.fecha_registro,
                    a.fecha_aprobacion,
                    a.impacta_nomina,
                    e.id as id,
                    e.nombre,
                    e.apellidos,
                    e.dni,
                    e.telefono,
                    e.numero_empleado,
                    e.cargo,
                    e.pago_por_hora,
                    e.pago_hora_especial,
                    e.tipo_jornada,
                    e.fecha_alta,
                    e.fecha_ingreso,
                    e.fecha_egreso,
                    e.motivo_egreso,
                    e.activo,
                    e.es_admin,
                    e.es_superadmin,
                    e.password_hash
                FROM ausencias a
                INNER JOIN empleados e ON a.empleado_id = e.id
                WHERE a.estado IN ('justificada', 'notificada')
                ORDER BY a.fecha_registro ASC
            """)

            resultados = []
            for row in cursor.fetchall():
                # Construir datos de ausencia con aliases
                row_dict = dict(row)
                ausencia_data = {
                    'id': row_dict['ausencia_id'],
                    'empleado_id': row_dict['ausencia_empleado_id'],
                    'fecha_inicio': row_dict['fecha_inicio'],
                    'fecha_fin': row_dict['fecha_fin'],
                    'tipo_ausencia': row_dict['tipo_ausencia'],
                    'subtipo': row_dict.get('subtipo'),
                    'estado': row_dict['estado'],
                    'es_notificacion_previa': row_dict.get('es_notificacion_previa'),
                    'motivo_empleado': row_dict.get('motivo_empleado'),
                    'documento_adjunto': row_dict.get('documento_adjunto'),
                    'aprobado_por': row_dict.get('aprobado_por'),
                    'observaciones_admin': row_dict.get('observaciones_admin'),
                    'fecha_registro': row_dict['fecha_registro'],
                    'fecha_aprobacion': row_dict.get('fecha_aprobacion'),
                    'impacta_nomina': row_dict.get('impacta_nomina')
                }

                # Construir datos de empleado (ya tiene el alias correcto para 'id')
                empleado_data = {
                    'id': row_dict['id'],
                    'nombre': row_dict['nombre'],
                    'apellidos': row_dict['apellidos'],
                    'dni': row_dict['dni'],
                    'telefono': row_dict['telefono'],
                    'numero_empleado': row_dict['numero_empleado'],
                    'cargo': row_dict.get('cargo'),
                    'pago_por_hora': row_dict.get('pago_por_hora'),
                    'pago_hora_especial': row_dict.get('pago_hora_especial'),
                    'tipo_jornada': row_dict['tipo_jornada'],
                    'fecha_alta': row_dict.get('fecha_alta'),
                    'fecha_ingreso': row_dict.get('fecha_ingreso'),
                    'fecha_egreso': row_dict.get('fecha_egreso'),
                    'motivo_egreso': row_dict.get('motivo_egreso'),
                    'activo': row_dict['activo'],
                    'es_admin': row_dict['es_admin'],
                    'es_superadmin': row_dict.get('es_superadmin'),
                    'password_hash': row_dict['password_hash']
                }

                ausencia = self._row_to_ausencia(ausencia_data)
                empleado = self._row_to_employee(empleado_data)
                resultados.append((ausencia, empleado))

            return resultados

    def aprobar_ausencia(self, ausencia_id: int, admin_id: int, observaciones: str = "") -> bool:
        """Aprueba una ausencia"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE ausencias
                SET estado = 'aprobada', aprobado_por = ?, observaciones_admin = ?, fecha_aprobacion = ?
                WHERE id = ?
            """, (admin_id, observaciones, datetime.now(), ausencia_id))

            return cursor.rowcount > 0

    def rechazar_ausencia(self, ausencia_id: int, admin_id: int, observaciones: str) -> bool:
        """Rechaza una ausencia"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE ausencias
                SET estado = 'rechazada', aprobado_por = ?, observaciones_admin = ?, fecha_aprobacion = ?
                WHERE id = ?
            """, (admin_id, observaciones, datetime.now(), ausencia_id))

            return cursor.rowcount > 0

    def crear_ausencia_pendiente(self, empleado_id: int, fecha: datetime) -> int:
        """Crea una ausencia pendiente de justificación (detección automática)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Verificar si ya existe una ausencia pendiente para esta fecha
            cursor.execute("""
                SELECT id FROM ausencias_pendientes
                WHERE empleado_id = ? AND date(fecha) = date(?)
            """, (empleado_id, fecha))

            if cursor.fetchone():
                return 0  # Ya existe

            cursor.execute("""
                INSERT INTO ausencias_pendientes (
                    empleado_id, fecha, detectada_automaticamente, fecha_deteccion, justificada
                ) VALUES (?, ?, 1, ?, 0)
            """, (empleado_id, fecha, datetime.now()))

            return cursor.lastrowid

    def obtener_ausencias_pendientes_justificar(self, empleado_id: int) -> List[AusenciaPendiente]:
        """Obtiene las ausencias pendientes de justificar de un empleado"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM ausencias_pendientes
                WHERE empleado_id = ? AND justificada = 0
                ORDER BY fecha DESC
            """, (empleado_id,))

            return [self._row_to_ausencia_pendiente(row) for row in cursor.fetchall()]

    def justificar_ausencia_pendiente(self, ausencia_pendiente_id: int) -> bool:
        """Marca una ausencia pendiente como justificada"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE ausencias_pendientes
                SET justificada = 1
                WHERE id = ?
            """, (ausencia_pendiente_id,))

            return cursor.rowcount > 0

    def verificar_ausencias_sin_justificar(self, empleado_id: int) -> bool:
        """Verifica si el empleado tiene ausencias pendientes de justificar"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM ausencias_pendientes
                WHERE empleado_id = ? AND justificada = 0
            """, (empleado_id,))

            count = cursor.fetchone()[0]
            return count > 0

    def _row_to_ausencia(self, row) -> Ausencia:
        """Convierte una fila de DB a objeto Ausencia"""
        return Ausencia(
            id=row['id'],
            empleado_id=row['empleado_id'],
            fecha_inicio=datetime.fromisoformat(row['fecha_inicio']) if row['fecha_inicio'] else None,
            fecha_fin=datetime.fromisoformat(row['fecha_fin']) if row['fecha_fin'] else None,
            tipo_ausencia=row['tipo_ausencia'],
            subtipo=row['subtipo'] or "",
            estado=row['estado'],
            es_notificacion_previa=bool(row['es_notificacion_previa']),
            motivo_empleado=row['motivo_empleado'] or "",
            documento_adjunto=row['documento_adjunto'] or "",
            aprobado_por=row['aprobado_por'],
            observaciones_admin=row['observaciones_admin'] or "",
            fecha_registro=datetime.fromisoformat(row['fecha_registro']) if row['fecha_registro'] else None,
            fecha_aprobacion=datetime.fromisoformat(row['fecha_aprobacion']) if row['fecha_aprobacion'] else None,
            impacta_nomina=row['impacta_nomina']
        )

    def _row_to_ausencia_pendiente(self, row) -> AusenciaPendiente:
        """Convierte una fila de DB a objeto AusenciaPendiente"""
        return AusenciaPendiente(
            id=row['id'],
            empleado_id=row['empleado_id'],
            fecha=datetime.fromisoformat(row['fecha']) if row['fecha'] else None,
            detectada_automaticamente=bool(row['detectada_automaticamente']),
            fecha_deteccion=datetime.fromisoformat(row['fecha_deteccion']) if row['fecha_deteccion'] else None,
            justificada=bool(row['justificada'])
        )

    # ==================== GESTIÓN DE DISPOSITIVOS ====================

    def registrar_dispositivo(self, dispositivo: DispositivoEmpleado) -> int:
        """Registra un nuevo dispositivo para un empleado"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO dispositivos_empleados (
                    empleado_id, device_fingerprint, device_info, fecha_registro
                ) VALUES (?, ?, ?, ?)
            """, (
                dispositivo.empleado_id,
                dispositivo.device_fingerprint,
                dispositivo.device_info,
                datetime.now()
            ))
            return cursor.lastrowid

    def obtener_dispositivos_empleado(self, empleado_id: int, solo_autorizados: bool = True) -> List[DispositivoEmpleado]:
        """Obtiene los dispositivos de un empleado"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if solo_autorizados:
                cursor.execute("""
                    SELECT * FROM dispositivos_empleados
                    WHERE empleado_id = ? AND autorizado = 1
                    ORDER BY fecha_ultimo_uso DESC
                """, (empleado_id,))
            else:
                cursor.execute("""
                    SELECT * FROM dispositivos_empleados
                    WHERE empleado_id = ?
                    ORDER BY fecha_registro DESC
                """, (empleado_id,))

            return [self._row_to_dispositivo(row) for row in cursor.fetchall()]

    def contar_dispositivos_autorizados(self, empleado_id: int) -> int:
        """Cuenta cuántos dispositivos autorizados tiene un empleado"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM dispositivos_empleados
                WHERE empleado_id = ? AND autorizado = 1
            """, (empleado_id,))
            return cursor.fetchone()[0]

    def verificar_dispositivo_autorizado(self, empleado_id: int, device_fingerprint: str) -> bool:
        """Verifica si un dispositivo está autorizado para un empleado"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id FROM dispositivos_empleados
                WHERE empleado_id = ? AND device_fingerprint = ? AND autorizado = 1
            """, (empleado_id, device_fingerprint))
            return cursor.fetchone() is not None

    def actualizar_ultimo_uso_dispositivo(self, empleado_id: int, device_fingerprint: str):
        """Actualiza la fecha de último uso de un dispositivo"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE dispositivos_empleados
                SET fecha_ultimo_uso = ?
                WHERE empleado_id = ? AND device_fingerprint = ?
            """, (datetime.now(), empleado_id, device_fingerprint))

    def revocar_dispositivo(self, dispositivo_id: int, admin_id: int) -> bool:
        """Revoca un dispositivo"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE dispositivos_empleados
                SET autorizado = 0, fecha_revocacion = ?, revocado_por = ?
                WHERE id = ?
            """, (datetime.now(), admin_id, dispositivo_id))
            return cursor.rowcount > 0

    def _row_to_dispositivo(self, row) -> DispositivoEmpleado:
        """Convierte una fila de DB a objeto DispositivoEmpleado"""
        return DispositivoEmpleado(
            id=row['id'],
            empleado_id=row['empleado_id'],
            device_fingerprint=row['device_fingerprint'],
            device_info=row['device_info'] or "",
            autorizado=bool(row['autorizado']),
            fecha_registro=datetime.fromisoformat(row['fecha_registro']) if row['fecha_registro'] else None,
            fecha_ultimo_uso=datetime.fromisoformat(row['fecha_ultimo_uso']) if row['fecha_ultimo_uso'] else None,
            fecha_revocacion=datetime.fromisoformat(row['fecha_revocacion']) if row['fecha_revocacion'] else None,
            revocado_por=row['revocado_por']
        )

    # ==================== GESTIÓN DE QR ====================

    def generar_qr_code(self) -> QRActivo:
        """Genera un nuevo código QR con TOTP"""
        import secrets
        import hashlib

        # Generar token único usando secretos criptográficos
        timestamp = str(datetime.now().timestamp())
        random_bytes = secrets.token_bytes(32)
        token_data = timestamp + random_bytes.hex()
        codigo_qr = hashlib.sha256(token_data.encode()).hexdigest()[:16]  # 16 caracteres

        # QR expira en 60 segundos
        fecha_generacion = datetime.now()
        fecha_expiracion = fecha_generacion + timedelta(seconds=60)

        qr = QRActivo(
            codigo_qr=codigo_qr,
            fecha_generacion=fecha_generacion,
            fecha_expiracion=fecha_expiracion,
            usado=False
        )

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO qr_activos (
                    codigo_qr, fecha_generacion, fecha_expiracion, usado
                ) VALUES (?, ?, ?, 0)
            """, (qr.codigo_qr, qr.fecha_generacion, qr.fecha_expiracion))
            qr.id = cursor.lastrowid

        return qr

    def validar_qr_code(self, codigo_qr: str) -> Optional[QRActivo]:
        """Valida si un código QR es válido y no ha expirado"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM qr_activos
                WHERE codigo_qr = ? AND usado = 0
            """, (codigo_qr,))

            row = cursor.fetchone()
            if not row:
                return None

            qr = self._row_to_qr(row)

            # Verificar si expiró
            if datetime.now() > qr.fecha_expiracion:
                return None

            return qr

    def marcar_qr_usado(self, codigo_qr: str, empleado_id: int) -> bool:
        """Marca un código QR como usado"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE qr_activos
                SET usado = 1, empleado_id = ?, fecha_uso = ?
                WHERE codigo_qr = ?
            """, (empleado_id, datetime.now(), codigo_qr))
            return cursor.rowcount > 0

    def limpiar_qr_expirados(self):
        """Elimina códigos QR expirados (más de 5 minutos)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            limite = datetime.now() - timedelta(minutes=5)
            cursor.execute("""
                DELETE FROM qr_activos
                WHERE fecha_expiracion < ?
            """, (limite,))

    def _row_to_qr(self, row) -> QRActivo:
        """Convierte una fila de DB a objeto QRActivo"""
        return QRActivo(
            id=row['id'],
            codigo_qr=row['codigo_qr'],
            fecha_generacion=datetime.fromisoformat(row['fecha_generacion']) if row['fecha_generacion'] else None,
            fecha_expiracion=datetime.fromisoformat(row['fecha_expiracion']) if row['fecha_expiracion'] else None,
            usado=bool(row['usado']),
            empleado_id=row['empleado_id'],
            fecha_uso=datetime.fromisoformat(row['fecha_uso']) if row['fecha_uso'] else None
        )

    # ==================== GESTIÓN DE DEPARTAMENTOS ====================

    def crear_departamento(self, departamento: Departamento) -> int:
        """Crea un nuevo departamento"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO departamentos (nombre, activo)
                VALUES (?, ?)
            """, (departamento.nombre, departamento.activo))
            return cursor.lastrowid

    def listar_departamentos(self, solo_activos: bool = True) -> List[Departamento]:
        """Lista los departamentos"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if solo_activos:
                cursor.execute("SELECT * FROM departamentos WHERE activo = 1 ORDER BY nombre")
            else:
                cursor.execute("SELECT * FROM departamentos ORDER BY nombre")
            return [self._row_to_departamento(row) for row in cursor.fetchall()]

    def actualizar_departamento(self, departamento: Departamento) -> bool:
        """Actualiza un departamento"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE departamentos
                SET nombre = ?, activo = ?
                WHERE id = ?
            """, (departamento.nombre, departamento.activo, departamento.id))
            return cursor.rowcount > 0

    def eliminar_departamento(self, departamento_id: int) -> bool:
        """Desactiva un departamento"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE departamentos SET activo = 0 WHERE id = ?", (departamento_id,))
            return cursor.rowcount > 0

    def _row_to_departamento(self, row) -> Departamento:
        """Convierte fila a objeto Departamento"""
        return Departamento(
            id=row['id'],
            nombre=row['nombre'],
            activo=bool(row['activo'])
        )

    # ==================== GESTIÓN DE UBICACIONES ====================

    def crear_ubicacion(self, ubicacion: Ubicacion) -> int:
        """Crea una nueva ubicación"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO ubicaciones (nombre, activo)
                VALUES (?, ?)
            """, (ubicacion.nombre, ubicacion.activo))
            return cursor.lastrowid

    def listar_ubicaciones(self, solo_activos: bool = True) -> List[Ubicacion]:
        """Lista las ubicaciones"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if solo_activos:
                cursor.execute("SELECT * FROM ubicaciones WHERE activo = 1 ORDER BY nombre")
            else:
                cursor.execute("SELECT * FROM ubicaciones ORDER BY nombre")
            return [self._row_to_ubicacion(row) for row in cursor.fetchall()]

    def actualizar_ubicacion(self, ubicacion: Ubicacion) -> bool:
        """Actualiza una ubicación"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE ubicaciones
                SET nombre = ?, activo = ?
                WHERE id = ?
            """, (ubicacion.nombre, ubicacion.activo, ubicacion.id))
            return cursor.rowcount > 0

    def eliminar_ubicacion(self, ubicacion_id: int) -> bool:
        """Desactiva una ubicación"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE ubicaciones SET activo = 0 WHERE id = ?", (ubicacion_id,))
            return cursor.rowcount > 0

    def _row_to_ubicacion(self, row) -> Ubicacion:
        """Convierte fila a objeto Ubicacion"""
        return Ubicacion(
            id=row['id'],
            nombre=row['nombre'],
            activo=bool(row['activo'])
        )
