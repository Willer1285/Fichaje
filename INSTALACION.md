# Guía de Instalación y Configuración

## Instalación Rápida (Windows)

### Método 1: Instalación Automática

1. Descargue el archivo `instalar.bat`
2. Haga doble clic en `instalar.bat`
3. Espere a que se complete la instalación
4. Ejecute `python main.py` para iniciar

### Método 2: Instalación Manual

```cmd
:: Crear entorno virtual
python -m venv venv

:: Activar entorno virtual
venv\Scripts\activate

:: Instalar dependencias
pip install -r requirements.txt

:: Ejecutar aplicación
python main.py
```

## Instalación Rápida (macOS/Linux)

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
python main.py
```

## Crear Ejecutable Independiente

### Windows

```bash
# Activar entorno virtual
venv\Scripts\activate

# Instalar dependencias de compilación
pip install pyinstaller

# Crear ejecutable
flet build windows

# El ejecutable estará en: build\windows\
```

### macOS

```bash
# Activar entorno virtual
source venv/bin/activate

# Crear ejecutable
flet build macos

# El ejecutable estará en: build/macos/
```

### Linux

```bash
# Activar entorno virtual
source venv/bin/activate

# Crear ejecutable
flet build linux

# El ejecutable estará en: build/linux/
```

## Configuración Inicial

### 1. Primera ejecución

Al ejecutar por primera vez, el sistema:
- Crea la base de datos `fichaje.db`
- Crea un usuario administrador por defecto

### 2. Credenciales por defecto

**Usuario Administrador:**
- DNI: `00000000A`
- Contraseña: `admin123`

### 3. Acciones recomendadas

1. Inicie sesión como administrador
2. Cambie la contraseña del administrador
3. Cree empleados reales
4. Elimine el usuario administrador de prueba (opcional)

## Personalización

### Cambiar tema de colores

Edite `main.py`, línea ~30:

```python
page.theme = ft.Theme(
    color_scheme_seed=ft.colors.BLUE_700,  # Cambiar color
    use_material3=True
)
```

### Cambiar tamaño de ventana

Edite `main.py`, líneas ~25-28:

```python
page.window_width = 900    # Ancho en píxeles
page.window_height = 700   # Alto en píxeles
```

## Backup y Restauración

### Hacer Backup

1. Copie el archivo `fichaje.db`
2. Guárdelo en un lugar seguro
3. Recomendación: backup semanal automático

```bash
# Ejemplo de backup automático (Windows)
copy fichaje.db backups\fichaje_%date:~-4,4%%date:~-10,2%%date:~-7,2%.db

# Ejemplo de backup automático (Linux/macOS)
cp fichaje.db backups/fichaje_$(date +%Y%m%d).db
```

### Restaurar Backup

1. Cierre la aplicación
2. Reemplace `fichaje.db` con el backup
3. Reinicie la aplicación

## Solución de Problemas

### Error: "No module named 'flet'"

```bash
# Asegúrese de tener el entorno virtual activado
pip install -r requirements.txt
```

### Error: "Permission denied" al crear fichaje.db

```bash
# Asegúrese de tener permisos de escritura
chmod +w .  # Linux/macOS
```

### La aplicación no inicia

1. Verifique que Python 3.8+ esté instalado
2. Verifique que todas las dependencias estén instaladas
3. Revise el archivo de log (si existe)

### Error al generar informes PDF

```bash
# Reinstale reportlab
pip uninstall reportlab
pip install reportlab
```

## Desinstalación

### Método 1: Manual

1. Elimine la carpeta del proyecto
2. Elimine el entorno virtual (carpeta `venv`)
3. Haga backup de `fichaje.db` si desea conservar los datos

### Método 2: Script

```bash
# Windows
rmdir /s venv
del fichaje.db

# Linux/macOS
rm -rf venv
rm fichaje.db
```

## Actualizaciones

### Actualizar dependencias

```bash
# Activar entorno virtual
source venv/bin/activate  # o venv\Scripts\activate en Windows

# Actualizar todas las dependencias
pip install --upgrade -r requirements.txt
```

### Actualizar el código

```bash
# Si usa git
git pull origin main

# Luego actualizar dependencias
pip install --upgrade -r requirements.txt
```

## Configuración para Producción

### 1. Seguridad

- Cambie todas las contraseñas por defecto
- Use contraseñas fuertes (mínimo 8 caracteres)
- Configure backups automáticos

### 2. Rendimiento

- La base de datos SQLite soporta miles de registros
- Haga limpieza periódica de registros antiguos (opcional)

### 3. Backup automático

Cree una tarea programada para backup diario:

**Windows (Programador de tareas):**
```cmd
copy "C:\ruta\fichaje.db" "C:\backups\fichaje_%date:~-4,4%%date:~-10,2%%date:~-7,2%.db"
```

**Linux (cron):**
```bash
0 2 * * * cp /ruta/fichaje.db /backups/fichaje_$(date +\%Y\%m\%d).db
```

## Preguntas Frecuentes

### ¿Puedo usar el sistema en red?

El sistema está diseñado para uso local en un solo equipo. Para uso en red, cada equipo debe tener su propia instalación.

### ¿Cuántos empleados soporta?

No hay límite práctico. Probado con más de 1000 empleados sin problemas.

### ¿Los informes son válidos legalmente?

Sí, cumplen con todos los requisitos del RD 8/2019.

---

Para más información, consulte el README.md
