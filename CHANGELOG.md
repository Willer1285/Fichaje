# Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [1.0.0] - 2026-01-14

### Añadido
- Sistema completo de fichaje para empleados
- Cumplimiento con Real Decreto-ley 8/2019
- Cumplimiento con RGPD (UE) 2016/679
- Interfaz gráfica moderna con Flet
- Sistema de autenticación seguro con bcrypt
- Gestión completa de empleados (CRUD)
- Soporte para jornada completa y parcial
- Fichaje de entrada/salida
- Fichaje de breaks (solo jornada completa)
- Cálculo automático de horas trabajadas
- Generación de informes en PDF
- Generación de informes en Excel
- Validación de DNI/NIE español
- Validación de teléfonos españoles
- Base de datos SQLite con trazabilidad
- Historial de modificaciones
- Panel de administrador
- Panel de empleado
- Documentación completa (README, INSTALACION, MANUAL_USO)
- Scripts de instalación automática (Windows, Linux, macOS)
- Scripts de ejecución rápida

### Características de Seguridad
- Contraseñas cifradas con bcrypt
- Validación de entrada en todos los formularios
- Control de acceso por roles (admin/empleado)
- Registro de auditoría de modificaciones
- Protección contra SQL injection
- Almacenamiento seguro de datos personales

### Características de Cumplimiento Legal
- Registro diario de inicio/fin de jornada
- Almacenamiento indefinido de registros
- Accesibilidad de registros para inspección
- Informes con formato válido para Inspección de Trabajo
- Trazabilidad completa de modificaciones
- Información al trabajador (RGPD)

### Características Técnicas
- Arquitectura modular y escalable
- Base de datos SQLite (sin servidor)
- Interfaz responsiva
- Animaciones fluidas
- Reloj en tiempo real
- Exportación múltiple (PDF, Excel)
- Multiplataforma (Windows, macOS, Linux)

## [Próximas Versiones]

### Planificado para v1.1.0
- [ ] Edición de fichajes por administrador con registro en historial
- [ ] Notificaciones de olvido de fichaje
- [ ] Gestión de vacaciones y ausencias
- [ ] Gráficos estadísticos de horas
- [ ] Modo oscuro
- [ ] Exportación a CSV
- [ ] Copias de seguridad automáticas
- [ ] Configuración de horarios laborales
- [ ] Cálculo de horas extra

### Considerado para v2.0.0
- [ ] Modo multi-empresa
- [ ] API REST para integraciones
- [ ] App móvil complementaria
- [ ] Reconocimiento facial (opcional, con consentimiento RGPD)
- [ ] Integración con sistemas de nómina
- [ ] Geolocalización opcional
- [ ] Firma digital de fichajes

---

Para más información sobre los cambios, consulte el repositorio del proyecto.
