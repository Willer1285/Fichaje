"""
Generador de códigos QR para autenticación de empleados
Sistema 100% offline para garantizar presencia física
"""

import qrcode
import io
import base64
import random
from datetime import datetime, timedelta
from typing import Optional, Tuple


class QRCodeGenerator:
    """Generador de códigos QR con códigos de 6 dígitos rotativos"""

    def __init__(self):
        self.codigo_actual = None
        self.timestamp_creacion = None
        self.duracion_codigo = 60  # segundos

    def generar_codigo_6_digitos(self) -> str:
        """
        Genera un código aleatorio de 6 dígitos numéricos.

        Returns:
            str: Código de 6 dígitos (ej: "742815")
        """
        return str(random.randint(100000, 999999))

    def crear_qr_real(self, codigo: str) -> str:
        """
        Crea un código QR real escaneable con el código de 6 dígitos.

        Args:
            codigo: Código de 6 dígitos a codificar en el QR

        Returns:
            str: Imagen QR en formato base64 para mostrar en Flet
        """
        # Crear objeto QR con configuración óptima
        qr = qrcode.QRCode(
            version=1,  # Tamaño mínimo (1 = 21x21)
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # Alta corrección de errores
            box_size=10,  # Tamaño de cada cuadrito
            border=4,  # Borde del QR
        )

        # Agregar el código de 6 dígitos como datos del QR
        qr.add_data(codigo)
        qr.make(fit=True)

        # Crear imagen del QR (blanco y negro)
        img = qr.make_image(fill_color="black", back_color="white")

        # Convertir a bytes para base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        # Convertir a base64 para Flet
        img_base64 = base64.b64encode(buffer.read()).decode('utf-8')

        return f"data:image/png;base64,{img_base64}"

    def generar_codigo_y_qr(self) -> Tuple[str, str]:
        """
        Genera un nuevo código de 6 dígitos y su código QR correspondiente.

        Returns:
            Tuple[str, str]: (código_6_digitos, imagen_qr_base64)
        """
        # Generar código aleatorio
        codigo = self.generar_codigo_6_digitos()

        # Crear QR real con el código
        qr_image = self.crear_qr_real(codigo)

        # Guardar código actual y timestamp
        self.codigo_actual = codigo
        self.timestamp_creacion = datetime.now()

        return codigo, qr_image

    def codigo_es_valido(self, codigo: str) -> bool:
        """
        Verifica si un código es válido (coincide y no ha expirado).

        Args:
            codigo: Código de 6 dígitos a validar

        Returns:
            bool: True si el código es válido, False si no
        """
        # Verificar que hay un código actual
        if not self.codigo_actual or not self.timestamp_creacion:
            return False

        # Verificar que el código coincide
        if codigo != self.codigo_actual:
            return False

        # Verificar que no ha expirado (60 segundos)
        ahora = datetime.now()
        tiempo_transcurrido = (ahora - self.timestamp_creacion).total_seconds()

        if tiempo_transcurrido > self.duracion_codigo:
            return False

        return True

    def obtener_tiempo_restante(self) -> int:
        """
        Obtiene el tiempo restante antes de que expire el código actual.

        Returns:
            int: Segundos restantes (0 si ya expiró)
        """
        if not self.timestamp_creacion:
            return 0

        ahora = datetime.now()
        tiempo_transcurrido = (ahora - self.timestamp_creacion).total_seconds()
        tiempo_restante = self.duracion_codigo - tiempo_transcurrido

        return max(0, int(tiempo_restante))

    def codigo_ha_expirado(self) -> bool:
        """
        Verifica si el código actual ha expirado.

        Returns:
            bool: True si ha expirado o no hay código, False si sigue válido
        """
        return self.obtener_tiempo_restante() == 0


# Instancia global del generador de QR
qr_generator = QRCodeGenerator()
