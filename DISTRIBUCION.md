# 📦 Guía de Distribución - Fichaje Zaragonjg
## Aplicación Nativa para Windows

---

## 🎯 **OPCIÓN 1: Ejecutable Portable (Más Rápido)**

### Requisitos previos:
- Python 3.9 o superior instalado
- Node.js 16 o superior instalado
- pip y npm actualizados

### Pasos para compilar:

1. **Abrir terminal en la carpeta del proyecto**
   ```bash
   cd C:\Users\wille\Downloads\Fichaje
   ```

2. **Ejecutar el script de compilación**
   ```bash
   python build_portable.py
   ```

3. **El ejecutable estará en:**
   ```
   dist/FichajeZaragonjg.exe
   ```

### Credenciales iniciales:
```
DNI: 00000000A
Contraseña: admin123
```

### Ubicación de datos:
```
C:\ProgramData\FichajeZaragonjg\
├── fichajes.db          (Base de datos)
└── assets\uploads\      (Fotos de empleados)
```

### Distribución:
- ✅ Puedes enviar **FichajeZaragonjg.exe** a cualquier usuario
- ✅ No necesita Python/Node instalado
- ✅ Hace doble clic y funciona
- ✅ Los datos se guardan automáticamente

---

## 🎯 **OPCIÓN 2: Instalador Profesional (Recomendado para producción)**

### ¿Por qué usar un instalador?
- ✅ Apariencia más profesional
- ✅ Crea accesos directos automáticamente
- ✅ Desinstalador incluido
- ✅ Registro en "Agregar/Quitar programas"
- ✅ Asistente de instalación paso a paso

### Requisitos adicionales:
- **Inno Setup** 6.x (gratuito)
- Descargar de: https://jrsoftware.org/isdl.php

### Pasos para crear el instalador:

1. **Compilar el ejecutable** (seguir pasos de Opción 1)

2. **Instalar Inno Setup**
   - Descargar e instalar desde el link anterior

3. **Abrir el archivo de configuración**
   - Abrir `installer.iss` con Inno Setup Compiler

4. **Compilar el instalador**
   - Click en "Build" → "Compile"
   - El instalador se creará en: `installer_output/FichajeZaragonjg_Setup_v1.0.0.exe`

5. **Distribuir el instalador**
   - Envía `FichajeZaragonjg_Setup_v1.0.0.exe` a tus clientes
   - Ellos solo ejecutan el instalador y listo

### Ventajas del instalador:
- 📌 Icono en el escritorio
- 📌 Acceso desde menú Inicio
- 📌 Desinstalación limpia
- 📌 Detección si la app está en ejecución
- 📌 Actualización fácil (reinstalar sobre versión anterior)

---

## 🔧 **Solución de Problemas**

### ❌ "Error: No se puede acceder" al hacer login

**Causa:** Base de datos no se creó o permisos insuficientes

**Solución:**
1. Ejecutar el .exe **como Administrador** (clic derecho → "Ejecutar como administrador")
2. Verificar que existe la carpeta:
   ```
   C:\ProgramData\FichajeZaragonjg\
   ```
3. Si no existe, crearla manualmente con permisos de escritura

### ❌ Ventana sin botones de minimizar/cerrar

**Causa:** `frameless=True` en desktop_app.py (YA CORREGIDO)

**Solución:** Ya está arreglado en el último commit. Recompilar:
```bash
python build_portable.py
```

### ❌ "Puerto 45678 ya en uso"

**Causa:** Otra instancia del programa corriendo

**Solución:**
1. Cerrar todas las ventanas de Fichaje
2. Abrir Task Manager (Ctrl+Shift+Esc)
3. Buscar "FichajeZaragonjg.exe" y finalizar proceso
4. Reiniciar la aplicación

### ❌ "No se encuentra frontend/dist"

**Causa:** Frontend no compilado

**Solución:**
```bash
cd frontend
npm install
npm run build
cd ..
```

---

## 🚀 **Mejoras Adicionales (Opcionales)**

### 1. **Firma Digital del Ejecutable**

**¿Por qué?**
- Evita advertencias de "Editor desconocido"
- Aumenta la confianza del usuario
- Previene alertas de Windows Defender

**Cómo:**
- Obtener certificado de firma de código (ej. DigiCert, Sectigo)
- Usar SignTool.exe de Windows SDK
- Comando:
  ```bash
  signtool sign /f certificado.pfx /p contraseña FichajeZaragonjg.exe
  ```

### 2. **Auto-actualización**

**Opciones:**
- **Squirrel.Windows** - Framework de actualización automática
- **WinSparkle** - Para aplicaciones nativas
- **Manual:** Verificar versión en servidor y descargar nueva

### 3. **Instalador NSIS (Alternativa a Inno Setup)**

**Ventajas:**
- Más personalizable
- Soporte para múltiples idiomas
- Mejor control sobre instalación

**Desventaja:**
- Más complejo que Inno Setup

---

## 📋 **Checklist de Distribución**

Antes de entregar a clientes, verifica:

- [ ] Compilar ejecutable con `python build_portable.py`
- [ ] Probar en máquina limpia (sin Python instalado)
- [ ] Verificar login con credenciales: `00000000A / admin123`
- [ ] Confirmar que la ventana tiene botones de minimizar/cerrar
- [ ] Probar creación de empleados
- [ ] Probar registro de fichajes
- [ ] Probar exportación PDF/Excel
- [ ] Verificar que datos persisten al cerrar/abrir app
- [ ] Crear instalador con Inno Setup (opcional pero recomendado)
- [ ] Documentar credenciales para el cliente
- [ ] Crear manual de usuario (opcional)

---

## 📄 **Estructura del Instalador**

```
FichajeZaragonjg_Setup_v1.0.0.exe
│
├─ Instalación:
│  ├─ C:\Program Files\Fichaje Zaragonjg\
│  │  └─ FichajeZaragonjg.exe
│  │
│  └─ C:\ProgramData\FichajeZaragonjg\
│     ├─ fichajes.db
│     └─ assets\uploads\
│
├─ Accesos directos:
│  ├─ Escritorio (opcional)
│  ├─ Menú Inicio
│  └─ Inicio Rápido (opcional)
│
└─ Desinstalador:
   └─ C:\Program Files\Fichaje Zaragonjg\unins000.exe
```

---

## 🎓 **Notas para el Cliente**

### Instalación:
1. Ejecutar `FichajeZaragonjg_Setup_v1.0.0.exe`
2. Seguir asistente de instalación
3. Abrir la aplicación desde el acceso directo
4. Iniciar sesión con:
   - **DNI:** 00000000A
   - **Contraseña:** admin123

### Primer uso:
1. **CAMBIAR la contraseña del administrador** inmediatamente
2. Crear empleados desde el panel de Empleados
3. Configurar turnos y horarios (si es necesario)
4. Comenzar a registrar fichajes

### Respaldo de datos:
**IMPORTANTE:** Hacer copias de seguridad periódicas de:
```
C:\ProgramData\FichajeZaragonjg\fichajes.db
C:\ProgramData\FichajeZaragonjg\assets\uploads\
```

Guardar estos archivos en ubicación segura (nube, disco externo, etc.)

---

## 🆘 **Soporte**

Para soporte técnico o dudas:
- GitHub: https://github.com/Willer1285/Fichaje
- Email: (agregar tu email de soporte)

---

**Versión:** 1.0.0
**Última actualización:** 2026-01-23
**Autor:** Willer Alberto Pacheco Alvarado
