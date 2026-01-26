import sys
import os
import io
import time
import base64
import json
import logging
import threading
import traceback

# =============================================================================
# PASO 0: Asegurar stdout/stderr ANTES de cualquier import que use logging
# En PyInstaller con console=False, sys.stdout y sys.stderr son None.
# Esto causa que uvicorn y otros modulos fallen silenciosamente al intentar
# escribir en stdout/stderr.
# =============================================================================
def _is_stream_writable(stream):
    """Verifica si un stream es valido y escribible."""
    if stream is None:
        return False
    try:
        if hasattr(stream, 'closed') and stream.closed:
            return False
        stream.write('')
        stream.flush()
        return True
    except (ValueError, OSError, AttributeError, TypeError):
        return False

def _ensure_safe_stdio():
    """
    Asegura que sys.stdout y sys.stderr sean objetos validos.
    En PyInstaller windowed (console=False), estos pueden ser None
    o file handles cerrados, lo que causa que uvicorn y logging
    fallen con 'I/O operation on closed file'.
    """
    if not _is_stream_writable(sys.stdout):
        sys.stdout = open(os.devnull, 'w', encoding='utf-8')
    if not _is_stream_writable(sys.stderr):
        sys.stderr = open(os.devnull, 'w', encoding='utf-8')

    # En Windows, reconfigurar con UTF-8 si tienen buffer
    if os.name == 'nt':
        try:
            if hasattr(sys.stdout, 'buffer') and not sys.stdout.closed:
                sys.stdout = io.TextIOWrapper(
                    sys.stdout.buffer, encoding='utf-8', errors='replace'
                )
        except (ValueError, OSError, AttributeError):
            pass
        try:
            if hasattr(sys.stderr, 'buffer') and not sys.stderr.closed:
                sys.stderr = io.TextIOWrapper(
                    sys.stderr.buffer, encoding='utf-8', errors='replace'
                )
        except (ValueError, OSError, AttributeError):
            pass

# Ejecutar INMEDIATAMENTE antes de cualquier import que use logging/print
_ensure_safe_stdio()

# =============================================================================
# PASO 1: Configurar path para importar el backend
# =============================================================================
if getattr(sys, 'frozen', False):
    # En modo ejecutable, PyInstaller maneja los imports
    pass
else:
    # En desarrollo, anadir carpeta backend
    backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
    sys.path.append(backend_path)

# Importar modulos del backend
import uvicorn
import webview
from app.main import app
from app.utils import paths
from app.utils.logger import setup_logging

# =============================================================================
# Filtro de logging para suprimir errores de AccessibilityObject de pywebview
# Estos errores son generados por EdgeChromium/WebView2 a traves de .NET
# y no afectan la funcionalidad de la aplicacion.
# =============================================================================
class AccessibilityErrorFilter(logging.Filter):
    """Filtra los errores de AccessibilityObject de pywebview/EdgeChromium."""
    def filter(self, record):
        if record.name == 'pywebview' and record.levelno >= logging.ERROR:
            msg = record.getMessage()
            if 'AccessibilityObject' in msg:
                return False
        return True

def safe_print(msg):
    """
    Funcion segura para imprimir mensajes.
    En modo ejecutable sin consola, stdout puede estar cerrado.
    """
    try:
        print(msg)
    except (ValueError, OSError, AttributeError):
        # Si stdout esta cerrado, usar logging como fallback
        try:
            logging.info(msg)
        except Exception:
            pass


class Api:
    def __init__(self):
        self.window = None

    def set_window(self, window):
        self.window = window

    def minimize(self):
        if self.window:
            self.window.minimize()

    def maximize(self):
        if self.window:
            if self.window.on_top:
                self.window.restore()
            else:
                self.window.maximize()

    def close(self):
        if self.window:
            self.window.destroy()

    def save_file(self, filename, content_base64):
        """
        Guarda un archivo en la carpeta de Descargas del usuario.
        Recibe el contenido en base64.
        """
        try:
            # Obtener ruta de descargas de forma compatible con Windows/Linux/Mac
            if os.name == 'nt':
                import winreg
                sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
                downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
                    downloads_path = winreg.QueryValueEx(key, downloads_guid)[0]
            else:
                downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')

            # Asegurar que el nombre de archivo sea seguro
            safe_filename = "".join([c for c in filename if c.isalpha() or c.isdigit() or c in (' ', '.', '_', '-')]).rstrip()
            file_path = os.path.join(downloads_path, safe_filename)

            # Manejar duplicados
            counter = 1
            name, ext = os.path.splitext(file_path)
            while os.path.exists(file_path):
                file_path = f"{name} ({counter}){ext}"
                counter += 1

            # Decodificar base64
            # El frontend puede enviar "data:application/pdf;base64,..."
            if ',' in content_base64:
                content_base64 = content_base64.split(',')[1]

            file_data = base64.b64decode(content_base64)

            with open(file_path, 'wb') as f:
                f.write(file_data)

            return {"success": True, "path": file_path}
        except Exception as e:
            return {"success": False, "error": str(e)}


# =============================================================================
# Variable global para comunicar estado del servidor entre hilos
# =============================================================================
_server_error = None
_server_started = threading.Event()

def start_server():
    """Inicia el servidor backend en el puerto 45678 con manejo robusto de errores."""
    global _server_error

    # Establecer variable de entorno para indicar modo desktop
    os.environ['DESKTOP_MODE'] = '1'

    logging.info("Iniciando servidor Uvicorn...")
    logging.info("   Host: 127.0.0.1")
    logging.info("   Puerto: 45678")

    try:
        # Usar Config y Server directamente para mejor control del ciclo de vida
        config = uvicorn.Config(
            app,
            host="127.0.0.1",
            port=45678,
            log_level="warning",  # Reducir logging de uvicorn para evitar problemas con stdio
            access_log=False,     # El middleware de FastAPI ya loguea requests
        )
        server = uvicorn.Server(config)

        # Senalizar que el servidor esta a punto de arrancar
        logging.info("Servidor Uvicorn configurado, iniciando...")
        server.run()
    except OSError as e:
        _server_error = f"Error de red al iniciar servidor: {e}"
        logging.error(f"Error de red al iniciar servidor: {e}")
        if "address already in use" in str(e).lower() or "10048" in str(e):
            logging.error("El puerto 45678 esta en uso. Puede haber otra instancia ejecutandose.")
            _server_error += " - Puerto 45678 en uso por otra aplicacion."
        logging.error(traceback.format_exc())
    except Exception as e:
        _server_error = f"Error inesperado al iniciar servidor: {e}"
        logging.error(f"Error inesperado al iniciar servidor: {e}")
        logging.error(traceback.format_exc())
    finally:
        # Senalizar que el hilo termino (con o sin error)
        _server_started.set()


def _get_error_html(error_msg):
    """Genera una pagina HTML de error para mostrar en webview cuando el servidor falla."""
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Error - Fichaje Zaragonjg</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #e0e0e0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }}
        .error-container {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 48px;
            max-width: 600px;
            text-align: center;
            backdrop-filter: blur(10px);
        }}
        .error-icon {{
            font-size: 64px;
            margin-bottom: 24px;
        }}
        h1 {{
            font-size: 24px;
            margin-bottom: 16px;
            color: #ff6b6b;
        }}
        p {{
            font-size: 16px;
            line-height: 1.6;
            margin-bottom: 12px;
            color: #b0b0b0;
        }}
        .error-detail {{
            background: rgba(255, 107, 107, 0.1);
            border: 1px solid rgba(255, 107, 107, 0.3);
            border-radius: 8px;
            padding: 16px;
            margin-top: 20px;
            font-family: 'Consolas', monospace;
            font-size: 13px;
            text-align: left;
            word-break: break-all;
            color: #ff9999;
        }}
        .suggestions {{
            margin-top: 24px;
            text-align: left;
        }}
        .suggestions li {{
            margin-bottom: 8px;
            padding-left: 8px;
        }}
    </style>
</head>
<body>
    <div class="error-container">
        <div class="error-icon">&#9888;</div>
        <h1>Error al iniciar el servidor</h1>
        <p>La aplicacion no pudo iniciar el servidor backend correctamente.</p>
        <div class="suggestions">
            <p><strong>Posibles soluciones:</strong></p>
            <ul>
                <li>Verifica que no haya otra instancia de la aplicacion ejecutandose</li>
                <li>Comprueba que el puerto 45678 no este en uso por otra aplicacion</li>
                <li>Reinicia la aplicacion</li>
                <li>Revisa los logs en: C:\\ProgramData\\FichajeZaragonjg\\logs\\</li>
            </ul>
        </div>
        <div class="error-detail">{error_msg}</div>
    </div>
</body>
</html>"""


if __name__ == '__main__':
    # Asegurar stdio seguro (ya ejecutado arriba, pero por si acaso)
    _ensure_safe_stdio()

    # Configurar logging al inicio
    try:
        log_file = setup_logging(log_to_file=True)

        # Aplicar filtro para suprimir errores de AccessibilityObject
        for handler in logging.getLogger().handlers:
            handler.addFilter(AccessibilityErrorFilter())
        # Tambien aplicar al logger de pywebview directamente
        pywebview_logger = logging.getLogger('pywebview')
        pywebview_logger.addFilter(AccessibilityErrorFilter())

        logging.info("="*80)
        logging.info("INICIANDO FICHAJE ZARAGONJG - VERSION DESKTOP")
        logging.info(f"Archivo de logs: {log_file}")
        logging.info(f"Modo: {'Ejecutable' if getattr(sys, 'frozen', False) else 'Desarrollo'}")
        logging.info(f"Python version: {sys.version}")
        logging.info(f"stdout type: {type(sys.stdout)}, stderr type: {type(sys.stderr)}")
        logging.info("="*80)
    except Exception as e:
        safe_print(f"Error configurando logging: {e}")
        safe_print("Continuando sin logging a archivo...")

    # Verificar si el frontend esta compilado
    dist_path = paths.get_frontend_dist_path()
    if not os.path.exists(dist_path):
        msg = f"ADVERTENCIA: No se encontro la carpeta '{dist_path}'."
        logging.warning(msg)
        safe_print(msg)
        safe_print("Por favor ejecuta 'cd frontend && npm run build' antes de iniciar la aplicacion.")

    # Iniciar el servidor backend en un hilo separado
    # daemon=True asegura que el hilo se cierre cuando el programa principal termine
    logging.info("Iniciando servidor backend en hilo separado...")
    t = threading.Thread(target=start_server)
    t.daemon = True
    t.start()

    # Esperar a que el servidor arranque (verificando el puerto)
    import socket
    start_time = time.time()
    server_ready = False
    max_wait = 30  # Aumentado a 30s para equipos lentos / antivirus
    logging.info("Esperando a que el servidor backend este listo...")

    while time.time() - start_time < max_wait:
        # Si el hilo del servidor murio con error, no seguir esperando
        if _server_error is not None:
            logging.error(f"Servidor fallo al iniciar: {_server_error}")
            break

        # Si el hilo ya no esta vivo y no hay error registrado, algo salio mal
        if not t.is_alive() and not server_ready:
            logging.error("El hilo del servidor termino inesperadamente")
            if _server_error is None:
                _server_error = "El servidor termino inesperadamente sin reportar error"
            break

        try:
            with socket.create_connection(("127.0.0.1", 45678), timeout=1.0):
                server_ready = True
                elapsed = time.time() - start_time
                logging.info(f"Servidor backend listo en {elapsed:.2f} segundos")
                break
        except (OSError, ConnectionRefusedError):
            time.sleep(0.3)

    if not server_ready and _server_error is None:
        _server_error = f"Timeout: el servidor no respondio en {max_wait} segundos"
        logging.warning(f"Advertencia: {_server_error}")

    # Crear instancia de la API
    api = Api()
    logging.info("Instancia de API creada para comunicacion con webview")

    # Determinar URL o HTML a cargar
    if server_ready:
        window_url = 'http://127.0.0.1:45678'
        window_html = None
        logging.info("Creando ventana de aplicacion...")
        logging.info(f"   URL: {window_url}")
    else:
        window_url = None
        window_html = _get_error_html(_server_error or "Error desconocido")
        logging.error("Mostrando pagina de error en ventana de aplicacion")

    logging.info(f"   Tamano: 1400x900")
    logging.info(f"   Frameless: False (barra Windows nativa)")

    # Crear la ventana nativa
    if window_url:
        window = webview.create_window(
            title='Fichaje Zaragonjg v1.0',
            url=window_url,
            width=1400,
            height=900,
            resizable=True,
            min_size=(1000, 700),
            js_api=api,
            frameless=False,
            easy_drag=False
        )
    else:
        window = webview.create_window(
            title='Fichaje Zaragonjg v1.0 - Error',
            html=window_html,
            width=700,
            height=600,
            resizable=True,
            min_size=(600, 500),
            frameless=False,
            easy_drag=False
        )

    api.set_window(window)

    # Iniciar el loop de la interfaz grafica
    logging.info("Iniciando aplicacion de escritorio...")

    # Configurar storage_path para evitar problemas de permisos con EdgeChromium
    try:
        if os.name == 'nt':
            storage_path = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'FichajeZaragonjg')
        else:
            storage_path = os.path.join(os.path.expanduser('~'), '.fichaje_zaragonjg')

        os.makedirs(storage_path, exist_ok=True)
        logging.info(f"Storage path configurado: {storage_path}")

        # Intentar con edgechromium primero, con fallback
        try:
            webview.start(gui='edgechromium', storage_path=storage_path, debug=False)
        except Exception as e:
            logging.warning(f"EdgeChromium fallo ({e}), intentando con GUI por defecto...")
            webview.start(storage_path=storage_path, debug=False)
    except Exception as e:
        logging.error(f"Error al configurar storage_path: {e}")
        try:
            webview.start(debug=False)
        except Exception as e2:
            logging.error(f"Error fatal al iniciar webview: {e2}")
            logging.error(traceback.format_exc())

    logging.info("Aplicacion cerrada por el usuario")
