"""
Sistema de logging para la aplicación
Escribe logs tanto a consola como a archivo
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logging(log_to_file=True, log_dir=None):
    """
    Configura el sistema de logging

    Args:
        log_to_file: Si True, escribe logs a archivo además de consola
        log_dir: Directorio donde guardar logs. Si None, usa directorio del proyecto
    """
    # Determinar directorio de logs
    if log_dir is None:
        # Intentar usar paths.py si existe
        try:
            from app.utils.paths import get_data_path
            log_dir = os.path.join(get_data_path(), "logs")
        except:
            # Fallback a directorio actual
            log_dir = os.path.join(os.getcwd(), "logs")

    # Crear directorio de logs si no existe
    os.makedirs(log_dir, exist_ok=True)

    # Nombre del archivo de log con fecha
    log_filename = f"fichaje_{datetime.now().strftime('%Y%m%d')}.log"
    log_filepath = os.path.join(log_dir, log_filename)

    # Configurar formato de logging
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'

    # Configurar root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Limpiar handlers existentes
    root_logger.handlers = []

    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(log_format, date_format)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # Handler para archivo (si está habilitado)
    if log_to_file:
        # RotatingFileHandler para limitar tamaño (10MB max, 5 backups)
        file_handler = RotatingFileHandler(
            log_filepath,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter(log_format, date_format)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

        # Log inicial
        logging.info("="*80)
        logging.info("INICIO DE SESIÓN DE LOGGING")
        logging.info(f"Archivo de log: {log_filepath}")
        logging.info(f"Modo: {'Producción (Desktop)' if getattr(sys, 'frozen', False) else 'Desarrollo'}")
        logging.info("="*80)

    return log_filepath

def get_logger(name):
    """Obtiene un logger con el nombre especificado"""
    return logging.getLogger(name)

# Para prints personalizados que también van al log
class LogPrint:
    """Clase para hacer print que también escribe al log"""

    def __init__(self, logger_name='app'):
        self.logger = logging.getLogger(logger_name)

    def __call__(self, *args, **kwargs):
        """Permite usar LogPrint() como función print()"""
        message = ' '.join(str(arg) for arg in args)
        self.logger.info(message)
        print(message, **kwargs)

# Instancia global para usar como print
log_print = LogPrint()
