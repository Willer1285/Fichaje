# Sistema de Fichaje para Empleados (V2)

Sistema moderno de registro de jornada laboral basado en **FastAPI** y **React**, cumpliendo con la normativa española:
- **Real Decreto-ley 8/2019**
- **Art. 34.9 del Estatuto de los Trabajadores**
- **RGPD (UE) 2016/679**

## 🚀 Características

### ✅ Cumplimiento Normativo
- ✓ Registro exacto de entradas, salidas y descansos
- ✓ Trazabilidad y almacenamiento seguro
- ✓ Informes PDF/Excel para Inspección de Trabajo

### 💻 Arquitectura Moderna
- **Backend**: API RESTful con Python + FastAPI
- **Frontend**: SPA con React + Tailwind CSS
- **Base de Datos**: SQLite (integrada y segura)

### 👥 Portal del Empleado
- Acceso mediante Código QR (Modo Kiosco)
- Panel de autogestión
- Solicitud de vacaciones y justificación de ausencias
- Consulta de historial personal

### 🛡️ Panel de Administración
- Gestión integral de personal
- Aprobación de solicitudes
- Generación de informes
- Configuración global del sistema

## 🛠️ Requisitos

- **Python**: 3.8+
- **Node.js**: 16+

## 📥 Instalación y Ejecución

El proyecto está dividido en dos componentes: Backend y Frontend.

### 1. Iniciar Backend (API)

```bash
cd backend
# Instalar dependencias
pip install -r requirements.txt
# Iniciar servidor
python -m uvicorn app.main:app --reload --port 8000
```

### 2. Iniciar Frontend (Interfaz Web)

En una nueva terminal:

```bash
cd frontend
# Instalar dependencias
npm install
# Iniciar servidor de desarrollo
npm run dev
```

Abra su navegador en: `http://localhost:5173`

## 🔑 Credenciales por Defecto

Al iniciar por primera vez, use estas credenciales de administrador:

- **DNI**: `00000000A`
- **Contraseña**: `admin123`

## 📁 Estructura del Proyecto

```
Fichaje/
├── backend/            # API FastAPI
│   ├── app/
│   │   ├── main.py     # Entry point
│   │   ├── routers/    # Endpoints (auth, attendance, reports...)
│   │   ├── database/   # Modelos y lógica DB
│   │   └── utils/      # Generadores PDF/QR, seguridad
│   └── requirements.txt
├── frontend/           # React App
│   ├── src/
│   │   ├── pages/      # Vistas (Dashboard, Login, Reports...)
│   │   └── App.jsx     # Enrutamiento principal
│   └── package.json
└── README.md
```

---
**Desarrollado con FastAPI + React**
