import os
import subprocess
import shutil
import sys
import platform

def run_command(command, cwd=None):
    print(f"Ejecutando: {command}")
    try:
        subprocess.check_call(command, shell=True, cwd=cwd)
    except subprocess.CalledProcessError as e:
        print(f"Error ejecutando comando: {e}")
        sys.exit(1)

def main():
    print("=== Iniciando construcción de TimeTrack Pro Portable ===")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(base_dir, "frontend")
    
    # 1. Instalar dependencias backend
    print("\n--- Instalando dependencias Backend ---")
    run_command(f'"{sys.executable}" -m pip install -r backend/requirements.txt')
    
    # Asegurar que pyinstaller está instalado
    run_command(f'"{sys.executable}" -m pip install pyinstaller')

    # 2. Construir Frontend
    print("\n--- Construyendo Frontend ---")
    # Verificar si node_modules existe, si no instalar
    if not os.path.exists(os.path.join(frontend_dir, "node_modules")):
        print("Instalando dependencias de Node...")
        run_command("npm install", cwd=frontend_dir)
    
    print("Compilando React...")
    run_command("npm run build", cwd=frontend_dir)
    
    # Verificar que dist existe
    dist_path = os.path.join(frontend_dir, "dist")
    if not os.path.exists(dist_path):
        print("Error: No se generó la carpeta frontend/dist")
        sys.exit(1)
        
    # 3. Empaquetar con PyInstaller
    print("\n--- Empaquetando con PyInstaller ---")
    
    # Definir separador de paths para --add-data
    sep = ';' if os.name == 'nt' else ':'
    
    # Datos a incluir: frontend/dist -> frontend/dist
    # Nota: PyInstaller espera src;dest
    add_data_list = [
        f"frontend/dist{sep}frontend/dist"
    ]
    
    # Incluir assets si existen
    if os.path.exists(os.path.join(base_dir, "assets")):
         add_data_list.append(f"assets{sep}assets")
         
    add_data_args = " ".join([f'--add-data "{item}"' for item in add_data_list])

    # Imports ocultos necesarios para Uvicorn y FastAPI
    hidden_imports = [
        "uvicorn.logging",
        "uvicorn.loops",
        "uvicorn.loops.auto",
        "uvicorn.protocols",
        "uvicorn.protocols.http",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.websockets",
        "uvicorn.protocols.websockets.auto",
        "uvicorn.lifespan",
        "uvicorn.lifespan.on",
        "email.mime.multipart",
        "email.mime.text",
        "email.mime.base",
        "email.mime.image",
        "email.mime.audio",
        "passlib.handlers.bcrypt"
    ]
    
    hidden_imports_args = " ".join([f"--hidden-import={mod}" for mod in hidden_imports])
    
    # Icono
    icon_path = os.path.join(base_dir, "assets", "icon.png")
    icon_option = f'--icon="{icon_path}"' if os.path.exists(icon_path) else ""
    
    # Rutas de búsqueda para PyInstaller (para que encuentre el paquete 'app' dentro de 'backend')
    paths_arg = f'--paths="{os.path.join(base_dir, "backend")}"'

    # Comando PyInstaller
    cmd = (
        f'pyinstaller --name="FichajeZaragonjg" --onefile --windowed --clean {icon_option} '
        f'{add_data_args} '
        f'{paths_arg} '
        f'{hidden_imports_args} '
        f'desktop_app.py'
    )
    
    run_command(cmd, cwd=base_dir)
    
    print("\n=== Construcción completada con éxito ===")
    exe_name = 'FichajeZaragonjg.exe' if os.name == 'nt' else 'FichajeZaragonjg'
    dist_file = os.path.join(base_dir, 'dist', exe_name)
    print(f"El ejecutable se encuentra en: {dist_file}")

if __name__ == "__main__":
    main()
