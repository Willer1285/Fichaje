# 📋 Guía de Logs - Fichaje Zaragonjg

## 📍 Ubicación de los Logs

Los logs de la aplicación desktop se guardan automáticamente en:

```
C:\ProgramData\FichajeZaragonjg\logs\
```

### Archivos de log:
- `fichaje_YYYYMMDD.log` - Log del día actual (ej: `fichaje_20260124.log`)
- Archivos antiguos se rotan automáticamente (máximo 5 backups de 10MB cada uno)

---

## 🔍 Cómo Ver los Logs

### Opción 1: Explorador de Windows
1. Presiona `Win + R`
2. Escribe: `C:\ProgramData\FichajeZaragonjg\logs`
3. Presiona Enter
4. Abre el archivo `.log` más reciente con Notepad

### Opción 2: Comando desde CMD/PowerShell
```cmd
# Ver los últimos logs
type C:\ProgramData\FichajeZaragonjg\logs\fichaje_*.log

# O con PowerShell
Get-Content C:\ProgramData\FichajeZaragonjg\logs\fichaje_*.log -Tail 50
```

### Opción 3: Notepad++
1. Abrir Notepad++
2. Archivo → Abrir
3. Navegar a `C:\ProgramData\FichajeZaragonjg\logs\`
4. Abrir el log más reciente

---

## 📖 Qué Contienen los Logs

Los logs registran:

### 🚀 Inicio de Aplicación
```
================================================================================
🚀 INICIANDO FICHAJE ZARAGONJG - VERSIÓN DESKTOP
📁 Archivo de logs: C:\ProgramData\FichajeZaragonjg\logs\fichaje_20260124.log
💻 Modo: Ejecutable
🐍 Python version: 3.13.x
================================================================================
```

### 💾 Inicialización de Base de Datos
```
💾 [DATABASE] Inicializando base de datos:
   Ruta: C:\ProgramData\FichajeZaragonjg\fichaje.db
   Existe: True/False
   Directorio: C:\ProgramData\FichajeZaragonjg
   Directorio existe: True
   Permisos escritura: True

🔑 [DB INIT] Verificando usuario administrador...
   ✅ Usuario administrador creado exitosamente
```

### 🔐 Intentos de Login
```
🔐 [LOGIN] Intento de inicio de sesión:
   DNI recibido: '00000000A'
   DNI normalizado: '00000000A'

🔍 [DB] Buscando empleado por DNI: '00000000A'
   ✓ Empleado encontrado en BD

✓ [LOGIN] Empleado encontrado:
   ID: 1
   Nombre: Admin Sistema
   DNI: 00000000A
   Activo: True
   Es admin: True
   Es superadmin: True

✓ [LOGIN] Contraseña verificada correctamente
✅ [LOGIN] Inicio de sesión exitoso para: Admin Sistema
```

### 📥 Requests HTTP
```
📥 POST /api/auth/login
✅ POST /api/auth/login - Status: 200 - Duration: 0.234s
```

### ❌ Errores
```
❌ [LOGIN] No se encontró empleado con DNI: 12345678X
❌ [LOGIN] Contraseña incorrecta para DNI: 00000000A
ERROR: Exception in ASGI application
```

---

## 🐛 Diagnóstico de Problemas

### Problema: Login falla en versión desktop

**Pasos:**
1. Abrir el archivo de log más reciente
2. Buscar la línea `🔐 [LOGIN] Intento de inicio de sesión:`
3. Revisar las líneas siguientes para ver dónde falla:
   - ✅ Empleado encontrado → Problema es la contraseña
   - ❌ No se encontró empleado → Problema es que no existe en BD o está inactivo
   - ✅ Contraseña verificada → Problema es permisos (no es admin)

### Problema: Base de datos no se crea

**Pasos:**
1. Buscar en log: `💾 [DATABASE] Inicializando base de datos:`
2. Verificar:
   - `Existe: False` → Primera vez, debería crearse
   - `Permisos escritura: False` → Error de permisos
3. Si hay error de permisos:
   - Ejecutar app como Administrador
   - O cambiar permisos de `C:\ProgramData\FichajeZaragonjg`

### Problema: Error al iniciar

**Pasos:**
1. Buscar líneas con `ERROR:` o `Exception`
2. Copiar el traceback completo
3. Compartir con soporte

---

## 🔄 Limpiar Logs Antiguos

Los logs se rotan automáticamente, pero si quieres limpiar manualmente:

```cmd
# Eliminar logs de más de 30 días
forfiles /P "C:\ProgramData\FichajeZaragonjg\logs" /S /M *.log /D -30 /C "cmd /c del @path"
```

---

## 📤 Compartir Logs para Soporte

Si necesitas ayuda:

1. **Copiar el log más reciente:**
   ```cmd
   copy C:\ProgramData\FichajeZaragonjg\logs\fichaje_*.log %USERPROFILE%\Desktop\
   ```

2. **O comprimir todos los logs:**
   ```powershell
   Compress-Archive -Path C:\ProgramData\FichajeZaragonjg\logs\*.log -DestinationPath %USERPROFILE%\Desktop\logs.zip
   ```

3. **Enviar el archivo** al equipo de soporte

---

## ⚙️ Configuración Avanzada

### Cambiar nivel de logging

Editar `/backend/app/utils/logger.py`:

```python
# Nivel INFO (por defecto) - logs normales
root_logger.setLevel(logging.INFO)

# Nivel DEBUG - logs muy detallados (puede ser lento)
root_logger.setLevel(logging.DEBUG)

# Nivel WARNING - solo advertencias y errores
root_logger.setLevel(logging.WARNING)
```

### Desactivar logging a archivo

En `desktop_app.py`, línea ~100:

```python
# Cambiar de True a False
log_file = setup_logging(log_to_file=False)
```

---

**Última actualización:** 2026-01-24
