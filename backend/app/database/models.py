"""
Modelos de datos del sistema de fichaje
Cumple con RD 8/2019 y RGPD
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class Departamento:
    """Modelo de departamento"""
    id: Optional[int] = None
    nombre: str = ""
    activo: bool = True

@dataclass
class Ubicacion:
    """Modelo de ubicación/sede"""
    id: Optional[int] = None
    nombre: str = ""
    activo: bool = True

@dataclass
class Employee:
    """Modelo de empleado"""
    id: Optional[int] = None
    # Campos de nombre separados
    primer_nombre: str = ""
    segundo_nombre: str = ""
    primer_apellido: str = ""
    segundo_apellido: str = ""
    # Campos legacy (se mantienen por compatibilidad, se calculan automáticamente)
    nombre: str = ""  # Se calcula como: primer_nombre + segundo_nombre
    apellidos: str = ""  # Se calcula como: primer_apellido + segundo_apellido
    dni: str = ""
    telefono: str = ""  # JSON list de teléfonos o string separado por comas
    email: str = ""  # Correo electrónico
    foto_path: str = ""  # Ruta a la foto del empleado
    numero_empleado: str = ""
    cargo: str = ""  # Cargo del empleado en la empresa
    departamento_id: Optional[int] = None  # ID del departamento
    ubicacion_id: Optional[int] = None  # ID de la ubicación
    turno_id: Optional[int] = None  # ID del turno/horario
    pago_por_hora: float = 0.0  # Monto por hora laboral normal
    pago_hora_especial: float = 0.0  # Monto por hora especial (horas extras, feriados, fines de semana)
    tipo_jornada: str = "completa"  # Mantenido por compatibilidad, idealmente usar turno_id
    es_admin: bool = False
    es_superadmin: bool = False  # Solo el superadmin puede eliminar usuarios
    password_hash: str = ""
    fecha_alta: Optional[datetime] = None  # Fecha de registro en sistema
    fecha_ingreso: Optional[datetime] = None  # Fecha de ingreso a la empresa
    activo: bool = True
    fecha_egreso: Optional[datetime] = None  # Fecha de salida de la empresa
    motivo_egreso: str = ""  # Motivo de salida (renuncia, despido, etc)

    @property
    def jornada_completa(self) -> bool:
        """Retorna True si el empleado tiene jornada completa"""
        return self.tipo_jornada == "completa"


@dataclass
class Fichaje:
    """Modelo de fichaje - Cumple con Art. 34.9 del Estatuto de los Trabajadores"""
    id: Optional[int] = None
    empleado_id: int = 0
    fecha: Optional[datetime] = None
    hora_entrada: Optional[datetime] = None
    hora_salida_break: Optional[datetime] = None
    hora_entrada_break: Optional[datetime] = None
    hora_salida: Optional[datetime] = None
    horas_trabajadas: float = 0.0
    tipo_fichaje: str = "normal"  # normal, feriado, fin_semana, salida_vacaciones, entrada_vacaciones, horas_extra
    horas_extras_aprobadas: float = 0.0  # Horas extras aprobadas por el admin
    aprobado_por: Optional[int] = None  # ID del admin que aprobó las horas extras
    modificado_por: Optional[int] = None  # ID del admin que modificó
    fecha_modificacion: Optional[datetime] = None
    observaciones: str = ""


@dataclass
class HistorialModificacion:
    """Registro de trazabilidad - Cumple con RGPD"""
    id: Optional[int] = None
    fichaje_id: int = 0
    empleado_id: int = 0
    modificado_por: int = 0
    fecha_modificacion: datetime = None
    campo_modificado: str = ""
    valor_anterior: str = ""
    valor_nuevo: str = ""
    motivo: str = ""


@dataclass
class Turno:
    """Modelo de turno laboral"""
    id: Optional[int] = None
    nombre: str = ""  # Ej: "Jornada parcial", "Turno nocturno"
    dias_semana: str = ""  # Días separados por coma: "Lunes,Martes,Miércoles"
    hora_inicio: str = "09:00"  # Formato HH:MM
    hora_fin: str = "17:00"  # Formato HH:MM
    activo: bool = True
    fecha_creacion: Optional[datetime] = None

    @property
    def lista_dias(self) -> List[str]:
        """Retorna lista de días del turno"""
        return [d.strip() for d in self.dias_semana.split(",") if d.strip()]

    @property
    def duracion_horas(self) -> float:
        """Calcula duración del turno en horas"""
        try:
            h_ini, m_ini = map(int, self.hora_inicio.split(":"))
            h_fin, m_fin = map(int, self.hora_fin.split(":"))
            inicio_min = h_ini * 60 + m_ini
            fin_min = h_fin * 60 + m_fin

            # Manejar turnos que cruzan medianoche
            if fin_min < inicio_min:
                fin_min += 24 * 60

            return (fin_min - inicio_min) / 60.0
        except:
            return 0.0


@dataclass
class Configuracion:
    """Configuración de la aplicación"""
    id: Optional[int] = None
    # Identificación de la aplicación
    nombre_aplicacion: str = "Fichaje"
    slogan: str = "Pro"  # Slogan o tagline debajo del nombre de la aplicación

    # Datos de la empresa/negocio
    nombre_empresa: str = ""
    representante_legal: str = ""
    dni_cif: str = ""
    direccion: str = ""
    ciudad: str = ""
    codigo_postal: str = ""
    pais: str = "España"
    telefono_empresa: str = ""
    email_empresa: str = ""  # Correo electrónico de la empresa

    # Rutas de archivos personalizados (relativos o Base64)
    logo_path: str = ""  # Ruta o datos Base64 del logo
    icono_path: str = ""  # Ruta o datos Base64 del icono de la ventana

    # Configuración de horas extras
    clave_aprobacion_horas_extras: str = "123456"  # Clave de 6 dígitos para aprobar horas extras

    # Configuración de llegadas tarde
    permitir_llegadas_tarde: bool = True
    tiempo_tolerancia_horas: int = 0  # Horas de tolerancia para llegadas tarde
    tiempo_tolerancia_minutos: int = 15  # Minutos de tolerancia para llegadas tarde

    # Configuración Regional
    zona_horaria: str = "Europe/Madrid" # Zona horaria (ej: Europe/Madrid, America/Caracas)
    moneda: str = "EUR" # Moneda del sistema (ej: EUR, USD)

    fecha_actualizacion: Optional[datetime] = None


@dataclass
class SolicitudVacacion:
    """Modelo de solicitud de vacaciones - Cumple con Art. 38 ET"""
    id: Optional[int] = None
    empleado_id: int = 0
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    dias_solicitados: float = 0.0
    tipo: str = "vacaciones_anuales"  # vacaciones_anuales, permiso_retribuido, permiso_sin_sueldo
    subtipo: str = ""  # matrimonio, nacimiento, fallecimiento, etc. (para permisos retribuidos)
    estado: str = "pendiente"  # pendiente, aprobada, rechazada
    motivo_empleado: str = ""
    aprobado_por: Optional[int] = None
    motivo_rechazo: str = ""
    fecha_solicitud: Optional[datetime] = None
    fecha_respuesta: Optional[datetime] = None


@dataclass
class SaldoVacaciones:
    """Modelo de saldo de vacaciones por empleado y año"""
    id: Optional[int] = None
    empleado_id: int = 0
    anio: int = 0
    dias_totales: float = 30.0  # 30 días según normativa española
    dias_consumidos: float = 0.0
    dias_pendientes: float = 30.0
    ultima_actualizacion: Optional[datetime] = None

    def actualizar_saldo(self):
        """Actualiza días pendientes"""
        self.dias_pendientes = self.dias_totales - self.dias_consumidos


@dataclass
class Ausencia:
    """Modelo de ausencia/permiso - Cumple con Art. 37 ET"""
    id: Optional[int] = None
    empleado_id: int = 0
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    tipo_ausencia: str = "ausencia_injustificada"  # baja_medica, permiso_retribuido, permiso_no_retribuido, ausencia_injustificada
    subtipo: str = ""  # matrimonio, nacimiento, fallecimiento, consulta_medica, etc.
    estado: str = "pendiente_justificar"  # notificada, pendiente_justificar, justificada, aprobada, rechazada
    es_notificacion_previa: bool = False  # True si empleado notificó antes de la ausencia
    motivo_empleado: str = ""
    documento_adjunto: str = ""  # Ruta o base64 del documento justificante
    aprobado_por: Optional[int] = None
    observaciones_admin: str = ""
    fecha_registro: Optional[datetime] = None
    fecha_aprobacion: Optional[datetime] = None
    impacta_nomina: str = "remunerado"  # remunerado, no_remunerado, it (incapacidad temporal)


@dataclass
class AusenciaPendiente:
    """Modelo de ausencia detectada automáticamente que necesita justificación"""
    id: Optional[int] = None
    empleado_id: int = 0
    fecha: Optional[datetime] = None  # Fecha en la que se detectó la ausencia
    detectada_automaticamente: bool = True
    fecha_deteccion: Optional[datetime] = None
    justificada: bool = False  # Se marca True cuando el empleado justifica


@dataclass
class DispositivoEmpleado:
    """Modelo de dispositivo autorizado por empleado"""
    id: Optional[int] = None
    empleado_id: int = 0
    device_fingerprint: str = ""  # Hash único del dispositivo
    device_info: str = ""  # Información legible del dispositivo (navegador, OS, etc)
    autorizado: bool = True
    fecha_registro: Optional[datetime] = None
    fecha_ultimo_uso: Optional[datetime] = None
    fecha_revocacion: Optional[datetime] = None
    revocado_por: Optional[int] = None  # ID del admin que revocó


@dataclass
class QRActivo:
    """Modelo de código QR activo"""
    id: Optional[int] = None
    codigo_qr: str = ""  # Token único generado con TOTP
    fecha_generacion: Optional[datetime] = None
    fecha_expiracion: Optional[datetime] = None  # Expira en 60 segundos
    usado: bool = False
    empleado_id: Optional[int] = None  # Se asigna cuando se usa
    fecha_uso: Optional[datetime] = None
