import uvicorn
import sys
import os

if __name__ == "__main__":
    # Añadir la carpeta backend al path de Python
    backend_path = os.path.join(os.getcwd(), "backend")
    sys.path.append(backend_path)
    
    print(f"Iniciando servidor desde: {backend_path}")
    
    # Ejecutar uvicorn apuntando al módulo app.main dentro de backend
    # Al añadir backend al path, 'app' se vuelve importable como top-level package
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True, reload_dirs=[backend_path])
