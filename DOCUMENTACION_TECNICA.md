# Documentación Técnica - TimeTrack Pro (V2)

Registro central de la arquitectura y componentes del sistema.

---

## 1. Arquitectura del Sistema

**TimeTrack Pro V2** es una aplicación web moderna basada en una arquitectura Cliente-Servidor separada.

### Stack Tecnológico
*   **Backend:** Python (FastAPI) + SQLite.
*   **Frontend:** React (Vite) + Tailwind CSS.
*   **Comunicación:** API RESTful (JSON).

---

## 2. Componentes del Sistema

### 2.1 Backend (`/backend`)
API RESTful que gestiona la lógica de negocio y persistencia.

*   **`app/main.py`**: Punto de entrada. Configura CORS y routers.
*   **`app/database/`**:
    *   `models.py`: Modelos Pydantic y definiciones de tablas.
    *   `db_manager.py`: Controlador de base de datos SQLite. Gestiona migraciones automáticas.
*   **`app/routers/`**: Módulos de la API.
    *   `auth.py`: Login (Admin y Empleado/QR).
    *   `attendance.py`: Fichaje (Entrada, Salida, Break), validaciones y estados.
    *   `employees.py`: CRUD de empleados.
    *   `requests.py`: Gestión de vacaciones y ausencias.
    *   `reports.py`: Generación de informes.
    *   `config.py`: Configuración global.
*   **`app/utils/`**:
    *   `report_generator.py`: Motor de generación PDF (ReportLab) y Excel (OpenPyXL).
    *   `qr_generator.py`: Generación de códigos QR rotativos.

### 2.2 Frontend (`/frontend`)
Single Page Application (SPA) para la interfaz de usuario.

*   **`src/App.jsx`**: Router principal y layout de Admin.
*   **`src/pages/`**:
    *   `Login.jsx`: Pantalla de acceso dual (Admin / QR Empleado).
    *   `EmployeeDashboard.jsx`: Panel exclusivo para empleados (Fichaje, Solicitudes).
    *   `Employees.jsx`: Gestión de personal (Admin).
    *   `Reports.jsx`: Generador de informes (Admin).
    *   `Config.jsx`: Ajustes del sistema (Admin).

---

## 3. Estado del Proyecto

### [V2.0.0] - Completado (20/01/2026)
**Migración Exitosa**
Se ha completado la transición desde la arquitectura legacy (Flet).
*   Eliminación total de código obsoleto.
*   Implementación de paridad funcional 100%.
*   Nuevo dashboard de empleado con autogestión.
*   Sistema de informes robusto.

---

## 4. Guía de Desarrollo

### Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```
