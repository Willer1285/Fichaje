"""
Configuración de tema y colores de marca TimeTrack Pro (Modern Style)
Estilo moderno, limpio y profesional.
"""

import flet as ft

# Colores modernos basados en el diseño "TimeTrack Pro"
class BrandColors:
    """Colores de marca modernos"""
    # Colores Principales
    PRIMARY = "#4318FF"       # Azul vibrante (Botones, Acentos, Sidebar activo)
    PRIMARY_HOVER = "#3311CC"
    SECONDARY = "#6AD2FF"     # Azul claro/cian
    
    # Sidebar
    SIDEBAR_BG = "#111C44"    # Azul muy oscuro para el sidebar
    SIDEBAR_TEXT = "#FFFFFF"
    SIDEBAR_TEXT_MUTED = "#A3AED0"

    # Colores de Fondo y Superficie
    BACKGROUND = "#F4F7FE"    # Gris azulado muy claro para el fondo principal
    SURFACE = "#FFFFFF"       # Blanco puro para tarjetas
    
    # Texto
    TEXT_PRIMARY = "#2B3674"  # Azul marino oscuro para títulos y texto principal
    TEXT_SECONDARY = "#A3AED0" # Gris azulado para subtítulos y textos secundarios
    DIVIDER = "#E0E5F2"

    # Colores de Estado (Modernos y suaves)
    SUCCESS = "#05CD99"       # Verde menta vibrante
    SUCCESS_LIGHT = "#E6FBF5" # Fondo verde muy claro para badges
    
    WARNING = "#FFB547"       # Naranja/Amarillo suave
    WARNING_LIGHT = "#FFF6E5"
    
    ERROR = "#EE5D50"         # Rojo coral suave
    ERROR_LIGHT = "#FEECEB"
    
    INFO = "#4318FF"          # Azul primario
    INFO_LIGHT = "#EFECFF"

    # Colores de compatibilidad (mapeados a la nueva paleta)
    PRIMARY_DARK = SIDEBAR_BG
    PRIMARY_DARK_HOVER = "#1B254B"
    PRIMARY_LIGHT = SECONDARY
    ACCENT_ORANGE = WARNING
    ACCENT_GREEN = SUCCESS

# Estilos de sombras
class Shadows:
    """Sombras modernas y suaves"""
    CARD = ft.BoxShadow(
        spread_radius=1,
        blur_radius=10,
        color=ft.Colors.with_opacity(0.05, "#000000"),
        offset=ft.Offset(0, 2)
    )
    CARD_HOVER = ft.BoxShadow(
        spread_radius=1,
        blur_radius=20,
        color=ft.Colors.with_opacity(0.1, "#000000"),
        offset=ft.Offset(0, 5)
    )

# Estilos de botones consistentes
class ButtonStyles:
    """Estilos de botones modernos"""
    BORDER_RADIUS = 16  # Bordes más redondeados para estilo moderno

    @staticmethod
    def primary():
        """Botón primario sólido"""
        return ft.ButtonStyle(
            bgcolor=BrandColors.PRIMARY,
            color=ft.Colors.WHITE,
            shape=ft.RoundedRectangleBorder(radius=ButtonStyles.BORDER_RADIUS),
            elevation=0,
            overlay_color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE)
        )

    @staticmethod
    def secondary():
        """Botón secundario/light"""
        return ft.ButtonStyle(
            bgcolor=ft.Colors.with_opacity(0.1, BrandColors.PRIMARY),
            color=BrandColors.PRIMARY,
            shape=ft.RoundedRectangleBorder(radius=ButtonStyles.BORDER_RADIUS),
            elevation=0
        )

    @staticmethod
    def action_success():
        """Botón de acción positiva"""
        return ft.ButtonStyle(
            bgcolor=BrandColors.SUCCESS,
            color=ft.Colors.WHITE,
            shape=ft.RoundedRectangleBorder(radius=ButtonStyles.BORDER_RADIUS),
            elevation=0
        )
        
    @staticmethod
    def action_danger():
        """Botón de acción destructiva"""
        return ft.ButtonStyle(
            bgcolor=ft.Colors.with_opacity(0.1, BrandColors.ERROR),
            color=BrandColors.ERROR,
            shape=ft.RoundedRectangleBorder(radius=ButtonStyles.BORDER_RADIUS),
            elevation=0
        )

    # Compatibilidad
    primary_light = secondary
    accent_orange = lambda: ft.ButtonStyle(bgcolor=BrandColors.WARNING, color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=16))
    accent_green = action_success
    
    @staticmethod
    def outlined():
        return ft.ButtonStyle(
            bgcolor=ft.Colors.TRANSPARENT,
            color=BrandColors.PRIMARY,
            shape=ft.RoundedRectangleBorder(radius=ButtonStyles.BORDER_RADIUS),
            side=ft.BorderSide(1, BrandColors.PRIMARY)
        )

# Estilos de texto
class TextStyles:
    """Estilos de tipografía"""
    @staticmethod
    def h1():
        return ft.TextStyle(size=24, weight=ft.FontWeight.BOLD, color=BrandColors.TEXT_PRIMARY)
    
    @staticmethod
    def h2():
        return ft.TextStyle(size=20, weight=ft.FontWeight.BOLD, color=BrandColors.TEXT_PRIMARY)
        
    @staticmethod
    def h3():
        return ft.TextStyle(size=16, weight=ft.FontWeight.BOLD, color=BrandColors.TEXT_PRIMARY)
        
    @staticmethod
    def body():
        return ft.TextStyle(size=14, color=BrandColors.TEXT_SECONDARY, weight=ft.FontWeight.W_500)
        
    @staticmethod
    def label():
        return ft.TextStyle(size=12, color=BrandColors.TEXT_SECONDARY)

# Estilos de contenedores
class ContainerStyles:
    """Estilos de contenedores"""
    BORDER_RADIUS = 20  # Tarjetas muy redondeadas
    
    @staticmethod
    def card():
        """Estilo base de tarjeta moderna"""
        return {
            "border_radius": ContainerStyles.BORDER_RADIUS,
            "bgcolor": BrandColors.SURFACE,
            "padding": 20,
            "shadow": Shadows.CARD
        }
