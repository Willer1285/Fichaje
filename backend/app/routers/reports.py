from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from app.dependencies import get_db
from app.utils.report_generator import ReportGenerator
from pydantic import BaseModel
from datetime import datetime
import os
import tempfile

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
        start = datetime.strptime(data.start_date, "%Y-%m-%d")
        end = datetime.strptime(data.end_date, "%Y-%m-%d")
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
        
        if data.type == "individual":
            if not data.employee_id:
                raise HTTPException(status_code=400, detail="Employee ID required")
            
            emp = db.obtener_empleado(data.employee_id)
            if not emp:
                raise HTTPException(status_code=404, detail="Empleado no encontrado")
                
            fichajes = db.obtener_fichajes_periodo(data.employee_id, start, end)
            
            if data.format == "pdf":
                generator.generar_pdf_empleado(emp, fichajes, start, end, filepath)
            else:
                generator.generar_excel_empleado(emp, fichajes, start, end, filepath)
                
        else:
            # Todos los empleados
            fichajes = db.obtener_todos_fichajes_periodo(start, end)
            
            if data.format == "pdf":
                 generator.generar_pdf_todos(fichajes, start, end, filepath)
            else:
                 generator.generar_excel_todos(fichajes, start, end, filepath)
            
        return FileResponse(filepath, filename=filename, media_type='application/octet-stream')

    except Exception as e:
        # En producción loguear error real
        print(f"Error generando reporte: {e}")
        raise HTTPException(status_code=500, detail=f"Error generando reporte: {str(e)}")
