@echo off
echo ========================================
echo   Deteniendo Fichaje - Sistema Completo
echo ========================================
echo.

REM Detener procesos de Python (Backend FastAPI)
echo [1/2] Deteniendo Backend (FastAPI)...
taskkill /F /FI "WINDOWTITLE eq Fichaje Backend - FastAPI*" 2>nul
if %errorlevel% == 0 (
    echo Backend detenido correctamente.
) else (
    echo Backend no estaba en ejecucion.
)

REM Detener procesos de Node/Vite (Frontend)
echo [2/2] Deteniendo Frontend (Vite)...
taskkill /F /FI "WINDOWTITLE eq Fichaje Frontend - Vite*" 2>nul
if %errorlevel% == 0 (
    echo Frontend detenido correctamente.
) else (
    echo Frontend no estaba en ejecucion.
)

echo.
echo ========================================
echo   Aplicacion detenida
echo ========================================
echo.
pause
