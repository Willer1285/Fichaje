@echo off
echo ========================================
echo   Iniciando Fichaje - Sistema Completo
echo ========================================
echo.

REM Iniciar Backend (FastAPI) en una ventana nueva
echo [1/2] Iniciando Backend (FastAPI)...
start "Fichaje Backend - FastAPI" cmd /k "cd /d %~dp0backend && python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

REM Esperar 5 segundos para que el backend inicie
echo Esperando a que el backend inicie...
timeout /t 5 /nobreak > nul

REM Iniciar Frontend (Vite) en una ventana nueva
echo [2/2] Iniciando Frontend (Vite)...
start "Fichaje Frontend - Vite" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ========================================
echo   Aplicacion iniciada correctamente!
echo ========================================
echo.
echo Backend (API):  http://127.0.0.1:8000
echo Frontend (Web): http://localhost:5173
echo.
echo Presiona cualquier tecla para cerrar esta ventana...
echo (Las ventanas del Backend y Frontend seguiran abiertas)
pause > nul
