import sys
import os
import pathlib

def get_base_path():
    """
    Retorna la ruta base de la aplicación (donde están los recursos estáticos).
    Si es un ejecutable (frozen), usa sys._MEIPASS.
    Si es desarrollo, usa la raíz del proyecto.
    """
    if getattr(sys, 'frozen', False):
        # Si estamos ejecutando desde PyInstaller
        return sys._MEIPASS
    else:
        # Si estamos en desarrollo (asumiendo que paths.py está en backend/app/utils/)
        # backend/app/utils/ -> ... -> Fichaje/
        return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

def get_data_path():
    """
    Retorna la ruta donde se deben guardar los datos persistentes (DB, uploads).
    Se utiliza C:\ProgramData\FichajeZaragonjg para centralizar los datos en el equipo,
    independientemente de dónde se ejecute el archivo .exe.
    """
    # Usamos ProgramData que es el estándar para datos de aplicación compartidos en Windows
    # y generalmente permite escritura sin permisos de administrador elevados (a diferencia de Program Files)
    if os.name == 'nt':
        base = os.environ.get('ProgramData', 'C:\\ProgramData')
    else:
        # Fallback para Linux/Mac (aunque la solicitud es para Windows)
        base = os.path.expanduser('~')
        
    path = os.path.join(base, "FichajeZaragonjg")
    
    # Asegurar que el directorio existe
    try:
        os.makedirs(path, exist_ok=True)
    except PermissionError:
        # Si falla (raro en ProgramData), intentar en AppData local del usuario
        base = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
        path = os.path.join(base, "FichajeZaragonjg")
        os.makedirs(path, exist_ok=True)
        
    return path

def get_frontend_dist_path():
    """Retorna la ruta a la carpeta dist del frontend"""
    # En desarrollo o en ejecutable, frontend/dist debe estar disponible
    # En ejecutable, se debe incluir como --add-data "frontend/dist;frontend/dist"
    # Por lo tanto, relative to base path, it is "frontend/dist"
    return os.path.join(get_base_path(), "frontend", "dist")

def get_uploads_path():
    """Retorna la ruta a la carpeta de uploads y asegura que exista"""
    # Los uploads deben ser persistentes
    # Usamos "assets/uploads" relativo a data_path
    # Ojo: backend original usa "backend/assets/uploads" o "assets/uploads" dependiendo de CWD
    # Vamos a estandarizar en "assets/uploads" en data_path
    path = os.path.join(get_data_path(), "assets", "uploads")
    os.makedirs(path, exist_ok=True)
    return path

def get_database_path(filename="fichaje.db"):
    """Retorna la ruta completa al archivo de base de datos"""
    return os.path.join(get_data_path(), filename)
