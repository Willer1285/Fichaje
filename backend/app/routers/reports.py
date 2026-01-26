from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from app.dependencies import get_db
from app.utils.report_generator import ReportGenerator
from pydantic import BaseModel
from datetime import datetime
import os
import tempfile
import logging

router = APIRouter(
    prefix="/api/reports",
    tags=["reports"],
)

class ReportRequest(BaseModel):
    type: str # individual, todos
    employee_id: int = None
    start_date: str # YYYY-MM-DD
    end_date: str
    format: str # pdf, excel

@router.post("/generate")
def generate_report(data: ReportRequest, db = Depends(get_db)):
    try:
        logging.info(f"\n📊 [REPORTS] Generando reporte:")
        logging.info(f"   Tipo: {data.type}")
        logging.info(f"   Formato: {data.format}")
        logging.info(f"   Fecha inicio: {data.start_date}")
        logging.info(f"   Fecha fin: {data.end_date}")
        logging.info(f"   Employee ID: {data.employee_id}")

        start = datetime.strptime(data.start_date, "%Y-%m-%d")
        # Asegurar que la fecha fin incluya todo el día (hasta 23:59:59)
        end = datetime.strptime(data.end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59, microsecond=999999)
        generator = ReportGenerator()

        # Generar nombre de archivo único
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"informe_{timestamp}"

        if data.format == "pdf":
            filename += ".pdf"
        else:
            filename += ".xlsx"

        # Usar directorio temporal del sistema
        temp_dir = tempfile.gettempdir()
        filepath = os.path.join(temp_dir, filename)
        logging.info(f"   📁 Filepath: {filepath}")

        if data.type == "individual":
            if not data.employee_id:
                raise HTTPException(status_code=400, detail="Employee ID required")

            emp = db.obtener_empleado(data.employee_id)
            if not emp:
                raise HTTPException(status_code=404, detail="Empleado no encontrado")

            logging.info(f"   👤 Empleado: {emp.nombre} {emp.apellidos}")
            fichajes = db.obtener_fichajes_periodo(data.employee_id, start, end)
            logging.info(f"   📋 Fichajes encontrados: {len(fichajes)}")

            if len(fichajes) > 0:
                logging.info(f"      Primer fichaje: fecha={fichajes[0].fecha}, horas={fichajes[0].horas_trabajadas}")
            else:
                logging.warning(f"      ⚠️ ADVERTENCIA: La lista de fichajes está vacía")

            logging.info(f"   🔄 Llamando a generador de {data.format} individual...")
            if data.format == "pdf":
                generator.generar_pdf_empleado(emp, fichajes, start, end, filepath)
            else:
                generator.generar_excel_empleado(emp, fichajes, start, end, filepath)

        else:
            # Todos los empleados
            fichajes = db.obtener_todos_fichajes_periodo(start, end)
            logging.info(f"   📋 Total fichajes (todos los empleados): {len(fichajes)}")

            if len(fichajes) > 0:
                logging.info(f"      Primer fichaje: fecha={fichajes[0][0].fecha}, empleado={fichajes[0][1].nombre}")
            else:
                logging.warning(f"      ⚠️ ADVERTENCIA: La lista de fichajes globales está vacía")

            logging.info(f"   🔄 Llamando a generador de {data.format} global...")
            if data.format == "pdf":
                 generator.generar_pdf_todos(fichajes, start, end, filepath)
            else:
                 generator.generar_excel_todos(fichajes, start, end, filepath)

        logging.info(f"✅ [REPORTS] Reporte generado exitosamente: {filename}")
        return FileResponse(filepath, filename=filename, media_type='application/octet-stream')

    except HTTPException as he:
        # Re-lanzar HTTPExceptions sin modificar
        raise he
    except Exception as e:
        # Loguear error completo con traceback
        logging.error(f"❌ [REPORTS] Error generando reporte: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generando reporte: {str(e)}")
