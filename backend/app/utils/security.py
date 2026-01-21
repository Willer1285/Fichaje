"""
Funciones de seguridad - Cumple con RGPD
Cifrado de contraseñas con bcrypt
"""

import bcrypt


def hash_password(password: str) -> str:
    """
    Genera un hash seguro de la contraseña usando bcrypt

    Args:
        password: Contraseña en texto plano

    Returns:
        Hash de la contraseña
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """
    Verifica una contraseña contra su hash

    Args:
        password: Contraseña en texto plano
        hashed: Hash almacenado

    Returns:
        True si la contraseña es correcta
    """
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False
