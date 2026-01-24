import webview
import threading
import uvicorn
import sys
import os
import time
import base64
import json

# Configurar path para importar el backend
if getattr(sys, 'frozen', False):
    # En modo ejecutable, PyInstaller maneja los imports
    pass
else:
    # En desarrollo, añadir carpeta backend
    backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
    sys.path.append(backend_path)

# Importar la instancia de FastAPI y utilidades
from app.main import app
from app.utils import paths

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
            if self.window.on_top: # No hay is_maximized directo fiable, pero toggleamos
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

def start_server():
    """Inicia el servidor backend en el puerto 45678"""
    # Usamos un puerto poco común para evitar conflictos
    # log_level="error" para no ensuciar la consola, a menos que haya problemas
    uvicorn.run(app, host="127.0.0.1", port=45678, log_level="info")

if __name__ == '__main__':
    # Verificar si el frontend está compilado
    dist_path = paths.get_frontend_dist_path()
    if not os.path.exists(dist_path):
        print(f"ADVERTENCIA: No se encontró la carpeta '{dist_path}'.")
        print("Por favor ejecuta 'cd frontend && npm run build' antes de iniciar la aplicación.")
        print("La aplicación intentará ejecutarse, pero el frontend no cargará correctamente.")

    # Iniciar el servidor backend en un hilo separado
    # daemon=True asegura que el hilo se cierre cuando el programa principal termine
    t = threading.Thread(target=start_server)
    t.daemon = True
    t.start()
    
    # Esperar a que el servidor arranque (verificando el puerto)
    import socket
    start_time = time.time()
    server_ready = False
    while time.time() - start_time < 15:
        try:
            with socket.create_connection(("127.0.0.1", 45678), timeout=0.5):
                server_ready = True
                break
        except (OSError, ConnectionRefusedError):
            time.sleep(0.1)
    
    if not server_ready:
        print("Advertencia: El servidor backend tarda en responder...")

    # Crear instancia de la API
    api = Api()
    
    # Crear la ventana nativa apuntando al servidor local
    # Esta ventana actuará como una aplicación de escritorio independiente del navegador del usuario
    window = webview.create_window(
        title='Fichaje Zaragonjg v1.0',
        url='http://127.0.0.1:45678',
        width=1400,
        height=900,
        resizable=True,
        min_size=(1000, 700),
        js_api=api,  # Exponer la API al frontend
        frameless=False,  # FALSE para mostrar barra de título de Windows
        easy_drag=False
    )
    
    api.set_window(window)

    # Iniciar el loop de la interfaz gráfica
    print("Iniciando aplicación de escritorio...")
    webview.start()
