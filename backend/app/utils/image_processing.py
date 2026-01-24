import os
import uuid
from pathlib import Path
from app.utils.paths import get_uploads_path

try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    print("Advertencia: OpenCV no está instalado. El procesamiento de imágenes (recorte de rostro) estará deshabilitado.")

# Directorio de subida - usar la ruta centralizada de ProgramData
UPLOAD_DIR = Path(get_uploads_path())

def process_employee_photo(file_bytes: bytes) -> str:
    """
    Procesa la foto del empleado:
    1. Detecta rostro y recorta cuadrado centrado.
    2. Si no detecta, recorta cuadrado central.
    3. Redimensiona a 400x400.
    4. Guarda en disco y retorna ruta.
    """
    # Generar nombre único
    filename = f"{uuid.uuid4()}.jpg"
    file_path = UPLOAD_DIR / filename

    if not OPENCV_AVAILABLE:
        # Guardar archivo tal cual si no hay OpenCV
        try:
            with open(file_path, "wb") as f:
                f.write(file_bytes)
            return f"/assets/uploads/{filename}"
        except Exception as e:
            print(f"Error guardando imagen sin procesar: {e}")
            return ""

    try:
        # Convertir bytes a array numpy
        nparr = np.frombuffer(file_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise ValueError("No se pudo decodificar la imagen")

        # Cargar clasificador de rostros pre-entrenado
        # OpenCV suele incluir estos xml en cv2.data.haarcascades
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) > 0:
            # Tomar el rostro más grande
            x, y, w, h = max(faces, key=lambda item: item[2] * item[3])
            
            # Calcular centro del rostro
            center_x, center_y = x + w // 2, y + h // 2
            
            # Definir tamaño del cuadro (usar el lado mayor del rostro con un margen)
            size = int(max(w, h) * 1.5)
            
            # Calcular coordenadas de recorte
            x1 = max(0, center_x - size // 2)
            y1 = max(0, center_y - size // 2)
            x2 = min(img.shape[1], center_x + size // 2)
            y2 = min(img.shape[0], center_y + size // 2)
            
            # Ajustar para ser cuadrado si toca bordes
            if x2 - x1 != y2 - y1:
                min_side = min(x2 - x1, y2 - y1)
                x2 = x1 + min_side
                y2 = y1 + min_side
                
            crop_img = img[y1:y2, x1:x2]
        else:
            # Recorte central
            h, w = img.shape[:2]
            min_side = min(h, w)
            start_x = (w - min_side) // 2
            start_y = (h - min_side) // 2
            crop_img = img[start_y:start_y+min_side, start_x:start_x+min_side]
            
        # Redimensionar
        final_img = cv2.resize(crop_img, (400, 400), interpolation=cv2.INTER_AREA)
        
        # Guardar
        cv2.imwrite(str(file_path), final_img)
        
        # Retornar ruta relativa para guardar en BD (usando forward slashes)
        return f"/assets/uploads/{filename}"
        
    except Exception as e:
        print(f"Error procesando imagen: {e}")
        # Intentar guardar sin procesar en caso de fallo de cv2
        try:
            with open(file_path, "wb") as f:
                f.write(file_bytes)
            return f"/assets/uploads/{filename}"
        except:
            return ""
