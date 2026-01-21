"""
Sistema de Iconos Profesionales - Font Awesome SVG
Reemplaza todos los iconos emoji/Material por Font Awesome profesionales
Marca: ZARAGONJG - FURNITURE DELIVERY
"""

import flet as ft
import base64


def crear_icono_svg(svg_content: str, size: int = 24, color: str = None) -> ft.Image:
    """Crea un icono a partir de contenido SVG de Font Awesome"""
    if color:
        svg_content = svg_content.replace('currentColor', color)

    svg_bytes = svg_content.encode('utf-8')
    svg_base64 = base64.b64encode(svg_bytes).decode('utf-8')

    return ft.Image(
        src=f"data:image/svg+xml;base64,{svg_base64}",
        width=size,
        height=size,
    )


# ==================== ICONOS SVG DE FONT AWESOME ====================

# Usuario / Admin
USER_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512" fill="currentColor">
<path d="M224 256c70.7 0 128-57.3 128-128S294.7 0 224 0 96 57.3 96 128s57.3 128 128 128zm-45.7 48C79.8 304 0 383.8 0 482.3 0 498.7 13.3 512 29.7 512h388.6c16.4 0 29.7-13.3 29.7-29.7 0-98.5-79.8-178.3-178.3-178.3h-91.4z"/>
</svg>'''

USER_SHIELD_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 512" fill="currentColor">
<path d="M224 256c70.7 0 128-57.3 128-128S294.7 0 224 0 96 57.3 96 128s57.3 128 128 128zm89.6 32h-16.7c-22.2 10.2-46.9 16-72.9 16s-50.6-5.8-72.9-16h-16.7C60.2 288 0 348.2 0 422.4V464c0 26.5 21.5 48 48 48h352c26.5 0 48-21.5 48-48v-41.6c0-74.2-60.2-134.4-134.4-134.4zm323-128.4l-27.8-28.1c-4.6-4.7-12.1-4.7-16.8-.1l-104.8 104-45.5-45.8c-4.6-4.7-12.1-4.7-16.8-.1l-28.1 27.9c-4.7 4.6-4.7 12.1-.1 16.8l81.7 82.3c4.6 4.7 12.1 4.7 16.8.1l141.3-140.2c4.6-4.7 4.7-12.2.1-16.8z"/>
</svg>'''

# Navegación
MENU_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512" fill="currentColor">
<path d="M0 96C0 78.3 14.3 64 32 64H416c17.7 0 32 14.3 32 32s-14.3 32-32 32H32C14.3 128 0 113.7 0 96zM0 256c0-17.7 14.3-32 32-32H416c17.7 0 32 14.3 32 32s-14.3 32-32 32H32c-17.7 0-32-14.3-32-32zM448 416c0 17.7-14.3 32-32 32H32c-17.7 0-32-14.3-32-32s14.3-32 32-32H416c17.7 0 32 14.3 32 32z"/>
</svg>'''

ARROW_LEFT_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512" fill="currentColor">
<path d="M9.4 233.4c-12.5 12.5-12.5 32.8 0 45.3l160 160c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3L109.2 288 416 288c17.7 0 32-14.3 32-32s-14.3-32-32-32l-306.7 0L214.6 118.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0l-160 160z"/>
</svg>'''

LOGOUT_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" fill="currentColor">
<path d="M377.9 105.9L500.7 228.7c7.2 7.2 11.3 17.1 11.3 27.3s-4.1 20.1-11.3 27.3L377.9 406.1c-6.4 6.4-15 9.9-24 9.9c-18.7 0-33.9-15.2-33.9-33.9l0-62.1-128 0c-17.7 0-32-14.3-32-32l0-64c0-17.7 14.3-32 32-32l128 0 0-62.1c0-18.7 15.2-33.9 33.9-33.9c9 0 17.6 3.6 24 9.9zM160 96L96 96c-17.7 0-32 14.3-32 32l0 256c0 17.7 14.3 32 32 32l64 0c17.7 0 32 14.3 32 32s-14.3 32-32 32l-64 0c-53 0-96-43-96-96L0 128C0 75 43 32 96 32l64 0c17.7 0 32 14.3 32 32s-14.3 32-32 32z"/>
</svg>'''

LOGIN_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" fill="currentColor">
<path d="M217.9 105.9L340.7 228.7c7.2 7.2 11.3 17.1 11.3 27.3s-4.1 20.1-11.3 27.3L217.9 406.1c-6.4 6.4-15 9.9-24 9.9c-18.7 0-33.9-15.2-33.9-33.9l0-62.1L32 320c-17.7 0-32-14.3-32-32l0-64c0-17.7 14.3-32 32-32l128 0 0-62.1c0-18.7 15.2-33.9 33.9-33.9c9 0 17.6 3.6 24 9.9zM512 416c0 35.3-28.7 64-64 64l-64 0c-17.7 0-32-14.3-32-32s14.3-32 32-32l64 0c17.7 0 32-14.3 32-32l0-256c0-17.7-14.3-32-32-32l-64 0c-17.7 0-32-14.3-32-32s14.3-32 32-32l64 0c35.3 0 64 28.7 64 64l0 256z"/>
</svg>'''

# Fichajes y tiempo
CLOCK_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" fill="currentColor">
<path d="M256 0a256 256 0 1 1 0 512A256 256 0 1 1 256 0zM232 120V256c0 8 4 15.5 10.7 20l96 64c11 7.4 25.9 4.4 33.3-6.7s4.4-25.9-6.7-33.3L280 243.2V120c0-13.3-10.7-24-24-24s-24 10.7-24 24z"/>
</svg>'''

CALENDAR_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512" fill="currentColor">
<path d="M96 32V64H48C21.5 64 0 85.5 0 112v48H448V112c0-26.5-21.5-48-48-48H352V32c0-17.7-14.3-32-32-32s-32 14.3-32 32V64H160V32c0-17.7-14.3-32-32-32S96 14.3 96 32zM448 192H0V464c0 26.5 21.5 48 48 48H400c26.5 0 48-21.5 48-48V192z"/>
</svg>'''

# Vacaciones / Beach
UMBRELLA_BEACH_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 512" fill="currentColor">
<path d="M346.3 271.8l-60.1-21.9L214 448H32c-17.7 0-32 14.3-32 32s14.3 32 32 32H544c17.7 0 32-14.3 32-32s-14.3-32-32-32H282.1l64.1-176.2zm121.1-.2l-3.3 9.1 67.7 24.6c18.1 6.6 38-4.2 39.6-23.4c6.5-78.5-23.9-155.5-80.8-208.5c2 8 3.2 16.3 3.4 24.8l.2 6c1.8 57-7.3 113.8-26.8 167.4zM462 99.1c-1.1-34.4-22.5-64.8-54.4-77.4c-.9-.4-1.9-.7-2.8-1.1c-33-11.7-69.8-2.4-93.1 23.8l-4 4.5C272.4 88.3 245 134.2 226.8 184l-3.3 9.1L434 269.7l3.3-9.1c18.1-49.8 26.6-102.5 24.9-155.5l-.2-6zM107.2 112.9c-11.1 15.7-2.8 36.8 15.3 43.4l71 25.8 3.3-9.1c19.5-53.6 49.1-103 87.1-145.5l4-4.5c6.2-6.9 13.1-13 20.5-18.2c-79.6 2.5-154.7 42.2-201.2 108z"/>
</svg>'''

# Ausencias / Hospital
HOSPITAL_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 512" fill="currentColor">
<path d="M232 0c-39.8 0-72 32.2-72 72v8H72C32.2 80 0 112.2 0 152V472c0 22.1 17.9 40 40 40H208c22.1 0 40-17.9 40-40V152c0-39.8-32.2-72-72-72V72c0-13.3 10.7-24 24-24h144c13.3 0 24 10.7 24 24v8c-39.8 0-72 32.2-72 72V472c0 22.1 17.9 40 40 40H600c22.1 0 40-17.9 40-40V152c0-39.8-32.2-72-72-72H480V72c0-39.8-32.2-72-72-72H232zM336 240c0-8.8 7.2-16 16-16h48V176c0-8.8 7.2-16 16-16h32c8.8 0 16 7.2 16 16v48h48c8.8 0 16 7.2 16 16v32c0 8.8-7.2 16-16 16H464v48c0 8.8-7.2 16-16 16H416c-8.8 0-16-7.2-16-16V288H352c-8.8 0-16-7.2-16-16V240z"/>
</svg>'''

# Empleados / People
PEOPLE_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 512" fill="currentColor">
<path d="M144 0a80 80 0 1 1 0 160A80 80 0 1 1 144 0zM512 0a80 80 0 1 1 0 160A80 80 0 1 1 512 0zM0 298.7C0 239.8 47.8 192 106.7 192h42.7c15.9 0 31 3.5 44.6 9.7c-1.3 7.2-1.9 14.7-1.9 22.3c0 38.2 16.8 72.5 43.3 96c-.2 0-.4 0-.7 0H21.3C9.6 320 0 310.4 0 298.7zM405.3 320c-.2 0-.4 0-.7 0c26.6-23.5 43.3-57.8 43.3-96c0-7.6-.7-15-1.9-22.3c13.6-6.3 28.7-9.7 44.6-9.7h42.7C592.2 192 640 239.8 640 298.7c0 11.8-9.6 21.3-21.3 21.3H405.3zM224 224a96 96 0 1 1 192 0 96 96 0 1 1 -192 0zM128 485.3C128 411.7 187.7 352 261.3 352H378.7C452.3 352 512 411.7 512 485.3c0 14.7-11.9 26.7-26.7 26.7H154.7c-14.7 0-26.7-11.9-26.7-26.7z"/>
</svg>'''

# Dispositivos / Phone
PHONE_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512" fill="currentColor">
<path d="M16 64C16 28.7 44.7 0 80 0H304c35.3 0 64 28.7 64 64V448c0 35.3-28.7 64-64 64H80c-35.3 0-64-28.7-64-64V64zM144 448c0 8.8 7.2 16 16 16h64c8.8 0 16-7.2 16-16s-7.2-16-16-16H160c-8.8 0-16 7.2-16 16zM304 64H80V384H304V64z"/>
</svg>'''

# QR Code
QRCODE_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512" fill="currentColor">
<path d="M0 80C0 53.5 21.5 32 48 32h96c26.5 0 48 21.5 48 48v96c0 26.5-21.5 48-48 48H48c-26.5 0-48-21.5-48-48V80zM64 96v64h64V96H64zM0 336c0-26.5 21.5-48 48-48h96c26.5 0 48 21.5 48 48v96c0 26.5-21.5 48-48 48H48c-26.5 0-48-21.5-48-48V336zm64 16v64h64V352H64zM304 32h96c26.5 0 48 21.5 48 48v96c0 26.5-21.5 48-48 48H304c-26.5 0-48-21.5-48-48V80c0-26.5 21.5-48 48-48zm80 64H320v64h64V96zM256 304c0-8.8 7.2-16 16-16h64c8.8 0 16 7.2 16 16s7.2 16 16 16h32c8.8 0 16-7.2 16-16s7.2-16 16-16s16 7.2 16 16v96c0 8.8-7.2 16-16 16H368c-8.8 0-16-7.2-16-16s-7.2-16-16-16s-16 7.2-16 16v64c0 8.8-7.2 16-16 16H272c-8.8 0-16-7.2-16-16V304zM368 480a16 16 0 1 1 0-32 16 16 0 1 1 0 32zm64 0a16 16 0 1 1 0-32 16 16 0 1 1 0 32z"/>
</svg>'''

# Informes / Chart
CHART_BAR_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" fill="currentColor">
<path d="M32 32c17.7 0 32 14.3 32 32V400c0 8.8 7.2 16 16 16H480c17.7 0 32 14.3 32 32s-14.3 32-32 32H80c-44.2 0-80-35.8-80-80V64C0 46.3 14.3 32 32 32zm96 96c0-17.7 14.3-32 32-32l192 0c17.7 0 32 14.3 32 32s-14.3 32-32 32l-192 0c-17.7 0-32-14.3-32-32zm32 64H288c17.7 0 32 14.3 32 32s-14.3 32-32 32H160c-17.7 0-32-14.3-32-32s14.3-32 32-32zm0 96H416c17.7 0 32 14.3 32 32s-14.3 32-32 32H160c-17.7 0-32-14.3-32-32s14.3-32 32-32z"/>
</svg>'''

# Configuración / Settings
SETTINGS_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" fill="currentColor">
<path d="M495.9 166.6c3.2 8.7 .5 18.4-6.4 24.6l-43.3 39.4c1.1 8.3 1.7 16.8 1.7 25.4s-.6 17.1-1.7 25.4l43.3 39.4c6.9 6.2 9.6 15.9 6.4 24.6c-4.4 11.9-9.7 23.3-15.8 34.3l-4.7 8.1c-6.6 11-14 21.4-22.1 31.2c-5.9 7.2-15.7 9.6-24.5 6.8l-55.7-17.7c-13.4 10.3-28.2 18.9-44 25.4l-12.5 57.1c-2 9.1-9 16.3-18.2 17.8c-13.8 2.3-28 3.5-42.5 3.5s-28.7-1.2-42.5-3.5c-9.2-1.5-16.2-8.7-18.2-17.8l-12.5-57.1c-15.8-6.5-30.6-15.1-44-25.4L83.1 425.9c-8.8 2.8-18.6 .3-24.5-6.8c-8.1-9.8-15.5-20.2-22.1-31.2l-4.7-8.1c-6.1-11-11.4-22.4-15.8-34.3c-3.2-8.7-.5-18.4 6.4-24.6l43.3-39.4C64.6 273.1 64 264.6 64 256s.6-17.1 1.7-25.4L22.4 191.2c-6.9-6.2-9.6-15.9-6.4-24.6c4.4-11.9 9.7-23.3 15.8-34.3l4.7-8.1c6.6-11 14-21.4 22.1-31.2c5.9-7.2 15.7-9.6 24.5-6.8l55.7 17.7c13.4-10.3 28.2-18.9 44-25.4l12.5-57.1c2-9.1 9-16.3 18.2-17.8C227.3 1.2 241.5 0 256 0s28.7 1.2 42.5 3.5c9.2 1.5 16.2 8.7 18.2 17.8l12.5 57.1c15.8 6.5 30.6 15.1 44 25.4l55.7-17.7c8.8-2.8 18.6-.3 24.5 6.8c8.1 9.8 15.5 20.2 22.1 31.2l4.7 8.1c6.1 11 11.4 22.4 15.8 34.3zM256 336a80 80 0 1 0 0-160 80 80 0 1 0 0 160z"/>
</svg>'''

# Estados: Check, X, Warning, Info
CHECK_CIRCLE_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" fill="currentColor">
<path d="M256 512A256 256 0 1 0 256 0a256 256 0 1 0 0 512zM369 209L241 337c-9.4 9.4-24.6 9.4-33.9 0l-64-64c-9.4-9.4-9.4-24.6 0-33.9s24.6-9.4 33.9 0l47 47L335 175c9.4-9.4 24.6-9.4 33.9 0s9.4 24.6 0 33.9z"/>
</svg>'''

TIMES_CIRCLE_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" fill="currentColor">
<path d="M256 512A256 256 0 1 0 256 0a256 256 0 1 0 0 512zM175 175c9.4-9.4 24.6-9.4 33.9 0l47 47 47-47c9.4-9.4 24.6-9.4 33.9 0s9.4 24.6 0 33.9l-47 47 47 47c9.4 9.4 9.4 24.6 0 33.9s-24.6 9.4-33.9 0l-47-47-47 47c-9.4 9.4-24.6 9.4-33.9 0s-9.4-24.6 0-33.9l47-47-47-47c-9.4-9.4-9.4-24.6 0-33.9z"/>
</svg>'''

WARNING_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" fill="currentColor">
<path d="M256 32c14.2 0 27.3 7.5 34.5 19.8l216 368c7.3 12.4 7.3 27.7 .2 40.1S486.3 480 472 480H40c-14.3 0-27.6-7.7-34.7-20.1s-7-27.8 .2-40.1l216-368C228.7 39.5 241.8 32 256 32zm0 128c-13.3 0-24 10.7-24 24V296c0 13.3 10.7 24 24 24s24-10.7 24-24V184c0-13.3-10.7-24-24-24zm32 224a32 32 0 1 0 -64 0 32 32 0 1 0 64 0z"/>
</svg>'''

INFO_CIRCLE_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" fill="currentColor">
<path d="M256 512A256 256 0 1 0 256 0a256 256 0 1 0 0 512zM216 336h24V272H216c-13.3 0-24-10.7-24-24s10.7-24 24-24h48c13.3 0 24 10.7 24 24v88h8c13.3 0 24 10.7 24 24s-10.7 24-24 24H216c-13.3 0-24-10.7-24-24s10.7-24 24-24zm40-208a32 32 0 1 1 0 64 32 32 0 1 1 0-64z"/>
</svg>'''

# Empresa / Building
BUILDING_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512" fill="currentColor">
<path d="M48 0C21.5 0 0 21.5 0 48V464c0 26.5 21.5 48 48 48h96V432c0-26.5 21.5-48 48-48s48 21.5 48 48v80h96c26.5 0 48-21.5 48-48V48c0-26.5-21.5-48-48-48H48zM64 240c0-8.8 7.2-16 16-16h32c8.8 0 16 7.2 16 16v32c0 8.8-7.2 16-16 16H80c-8.8 0-16-7.2-16-16V240zm112-16h32c8.8 0 16 7.2 16 16v32c0 8.8-7.2 16-16 16H176c-8.8 0-16-7.2-16-16V240c0-8.8 7.2-16 16-16zm80 16c0-8.8 7.2-16 16-16h32c8.8 0 16 7.2 16 16v32c0 8.8-7.2 16-16 16H272c-8.8 0-16-7.2-16-16V240zM80 96h32c8.8 0 16 7.2 16 16v32c0 8.8-7.2 16-16 16H80c-8.8 0-16-7.2-16-16V112c0-8.8 7.2-16 16-16zm80 16c0-8.8 7.2-16 16-16h32c8.8 0 16 7.2 16 16v32c0 8.8-7.2 16-16 16H176c-8.8 0-16-7.2-16-16V112zM272 96h32c8.8 0 16 7.2 16 16v32c0 8.8-7.2 16-16 16H272c-8.8 0-16-7.2-16-16V112c0-8.8 7.2-16 16-16z"/>
</svg>'''

# Archivo / File
FILE_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512" fill="currentColor">
<path d="M320 464c8.8 0 16-7.2 16-16V160H256c-17.7 0-32-14.3-32-32V48H64c-8.8 0-16 7.2-16 16V448c0 8.8 7.2 16 16 16H320zM0 64C0 28.7 28.7 0 64 0H229.5c17 0 33.3 6.7 45.3 18.7l90.5 90.5c12 12 18.7 28.3 18.7 45.3V448c0 35.3-28.7 64-64 64H64c-35.3 0-64-28.7-64-64V64z"/>
</svg>'''


# ==================== FUNCIONES HELPER ====================

def icono_menu(size: int = 24, color: str = "#FFFFFF") -> ft.Image:
    """Icono de menú hamburguesa"""
    return crear_icono_svg(MENU_SVG, size, color)

def icono_usuario_svg(size: int = 24, color: str = "#FFFFFF") -> ft.Image:
    """Icono de usuario"""
    return crear_icono_svg(USER_SVG, size, color)

def icono_usuario_shield(size: int = 24, color: str = "#FFFFFF") -> ft.Image:
    """Icono de usuario con escudo (admin)"""
    return crear_icono_svg(USER_SHIELD_SVG, size, color)

def icono_arrow_left(size: int = 24, color: str = "#FFFFFF") -> ft.Image:
    """Icono de flecha izquierda"""
    return crear_icono_svg(ARROW_LEFT_SVG, size, color)

def icono_logout(size: int = 24, color: str = "#FFFFFF") -> ft.Image:
    """Icono de logout/cerrar sesión"""
    return crear_icono_svg(LOGOUT_SVG, size, color)

def icono_login(size: int = 24, color: str = "#FFFFFF") -> ft.Image:
    """Icono de login"""
    return crear_icono_svg(LOGIN_SVG, size, color)

def icono_clock(size: int = 24, color: str = "#2C5F7F") -> ft.Image:
    """Icono de reloj/fichajes"""
    return crear_icono_svg(CLOCK_SVG, size, color)

def icono_calendar(size: int = 24, color: str = "#2C5F7F") -> ft.Image:
    """Icono de calendario"""
    return crear_icono_svg(CALENDAR_SVG, size, color)

def icono_vacaciones(size: int = 24, color: str = "#4A9FD8") -> ft.Image:
    """Icono de vacaciones"""
    return crear_icono_svg(UMBRELLA_BEACH_SVG, size, color)

def icono_ausencias(size: int = 24, color: str = "#E85D3C") -> ft.Image:
    """Icono de ausencias/hospital"""
    return crear_icono_svg(HOSPITAL_SVG, size, color)

def icono_empleados(size: int = 24, color: str = "#2C5F7F") -> ft.Image:
    """Icono de empleados/personas"""
    return crear_icono_svg(PEOPLE_SVG, size, color)

def icono_dispositivos(size: int = 24, color: str = "#4A9FD8") -> ft.Image:
    """Icono de dispositivos/teléfono"""
    return crear_icono_svg(PHONE_SVG, size, color)

def icono_qrcode(size: int = 24, color: str = "#7CB342") -> ft.Image:
    """Icono de código QR"""
    return crear_icono_svg(QRCODE_SVG, size, color)

def icono_informes(size: int = 24, color: str = "#7CB342") -> ft.Image:
    """Icono de informes/gráficos"""
    return crear_icono_svg(CHART_BAR_SVG, size, color)

def icono_configuracion(size: int = 24, color: str = "#E85D3C") -> ft.Image:
    """Icono de configuración"""
    return crear_icono_svg(SETTINGS_SVG, size, color)

def icono_check_circle(size: int = 24, color: str = "#7CB342") -> ft.Image:
    """Icono de check/correcto"""
    return crear_icono_svg(CHECK_CIRCLE_SVG, size, color)

def icono_times_circle(size: int = 24, color: str = "#E85D3C") -> ft.Image:
    """Icono de X/error"""
    return crear_icono_svg(TIMES_CIRCLE_SVG, size, color)

def icono_warning(size: int = 24, color: str = "#FF9800") -> ft.Image:
    """Icono de advertencia"""
    return crear_icono_svg(WARNING_SVG, size, color)

def icono_info(size: int = 24, color: str = "#4A9FD8") -> ft.Image:
    """Icono de información"""
    return crear_icono_svg(INFO_CIRCLE_SVG, size, color)

def icono_empresa(size: int = 24, color: str = "#2C5F7F") -> ft.Image:
    """Icono de edificio/empresa"""
    return crear_icono_svg(BUILDING_SVG, size, color)

def icono_file(size: int = 24, color: str = "#757575") -> ft.Image:
    """Icono de archivo"""
    return crear_icono_svg(FILE_SVG, size, color)


def icono_logo(size: int = 100, color: str = "#2C5F7F") -> ft.Image:
    """Icono del logo principal (usado cuando no hay imagen)"""
    return crear_icono_svg(BUILDING_SVG, size, color)


# Mantener compatibilidad con código anterior
def icono_reloj(size: int = 24, color: str = "#2C5F7F") -> ft.Image:
    """Alias para icono_clock"""
    return icono_clock(size, color)

def icono_ban(size: int = 24, color: str = "#E85D3C") -> ft.Image:
    """Alias para icono_times_circle"""
    return icono_times_circle(size, color)

def icono_error(size: int = 24, color: str = "#E85D3C") -> ft.Image:
    """Alias para icono_times_circle"""
    return icono_times_circle(size, color)


def icono_usuario(es_admin: bool = False, es_superadmin: bool = False, size: int = 40) -> ft.Container:
    """
    Crea un icono profesional para usuario con bordes cuadrados redondeados
    Compatible con el tema de la marca ZARAGONJG
    """
    from app.utils.theme import BrandColors, ButtonStyles

    if es_superadmin:
        texto = "SA"
        bgcolor = BrandColors.ACCENT_ORANGE
        tooltip = "Superadministrador"
    elif es_admin:
        texto = "AD"
        bgcolor = BrandColors.PRIMARY_DARK
        tooltip = "Administrador"
    else:
        texto = "EM"
        bgcolor = BrandColors.ACCENT_GREEN
        tooltip = "Empleado"

    return ft.Container(
        content=ft.Text(
            texto,
            size=size * 0.4,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.WHITE
        ),
        width=size,
        height=size,
        bgcolor=bgcolor,
        border_radius=ButtonStyles.BORDER_RADIUS,  # Bordes cuadrados redondeados, no circulares
        alignment=ft.Alignment(0, 0),
        tooltip=tooltip
    )
