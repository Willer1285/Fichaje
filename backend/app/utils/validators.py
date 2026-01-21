"""
Validadores de datos
Cumple con normativa española
"""

import re
from typing import Tuple


def validar_dni(dni: str) -> Tuple[bool, str]:
    """
    Valida un DNI/NIE español

    Returns:
        (es_valido, mensaje_error)
    """
    dni = dni.upper().strip()

    # Validar formato
    if not re.match(r'^[XYZ0-9]\d{7}[A-Z]$', dni):
        return False, "Formato de DNI/NIE incorrecto"

    # Validar letra
    letras = 'TRWAGMYFPDXBNJZSQVHLCKE'

    if dni[0] in 'XYZ':
        # NIE
        nie_map = {'X': '0', 'Y': '1', 'Z': '2'}
        numero = int(nie_map[dni[0]] + dni[1:8])
    else:
        # DNI
        numero = int(dni[:8])

    letra_correcta = letras[numero % 23]

    if dni[-1] != letra_correcta:
        return False, "La letra del DNI/NIE no es correcta"

    return True, ""


def validar_telefono(telefono: str) -> Tuple[bool, str]:
    """
    Valida un teléfono español

    Returns:
        (es_valido, mensaje_error)
    """
    telefono = telefono.strip().replace(" ", "").replace("-", "")

    # Formato español (móvil o fijo)
    if not re.match(r'^(\+34|0034)?[6789]\d{8}$', telefono):
        return False, "Formato de teléfono incorrecto (ej: 612345678)"

    return True, ""


def validar_password(password: str) -> Tuple[bool, str]:
    """
    Valida la fortaleza de una contraseña

    Returns:
        (es_valido, mensaje_error)
    """
    if len(password) < 6:
        return False, "La contraseña debe tener al menos 6 caracteres"

    if len(password) > 128:
        return False, "La contraseña es demasiado larga"

    return True, ""


def validar_nombre(nombre: str) -> Tuple[bool, str]:
    """
    Valida un nombre

    Returns:
        (es_valido, mensaje_error)
    """
    nombre = nombre.strip()

    if len(nombre) < 2:
        return False, "El nombre debe tener al menos 2 caracteres"

    if len(nombre) > 100:
        return False, "El nombre es demasiado largo"

    if not re.match(r'^[a-záéíóúñA-ZÁÉÍÓÚÑ\s]+$', nombre):
        return False, "El nombre solo puede contener letras"

    return True, ""
