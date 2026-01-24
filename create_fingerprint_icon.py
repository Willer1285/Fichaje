#!/usr/bin/env python3
"""
Script para crear un icono de huella digital para la aplicación
Genera un archivo .ico compatible con PyInstaller en Windows
"""
from PIL import Image, ImageDraw
import os

def create_fingerprint_icon(output_path="assets/fingerprint.ico", sizes=[16, 32, 48, 64, 128, 256]):
    """Crea un icono de huella digital en múltiples tamaños"""

    # Crear lista de imágenes en diferentes tamaños para el .ico
    images = []

    for size in sizes:
        # Crear imagen con fondo transparente
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Colores (azul primario de la app)
        primary_color = (59, 130, 246, 255)  # #3B82F6 - blue-500
        secondary_color = (37, 99, 235, 255)  # #2563EB - blue-600

        # Margen proporcional al tamaño
        margin = size // 8
        center_x = size // 2
        center_y = size // 2

        # Radio base de la huella
        base_radius = (size - margin * 2) // 2

        # Dibujar arcos concéntricos para simular huella digital
        num_arcs = 5
        line_width = max(1, size // 32)

        for i in range(num_arcs):
            radius = base_radius - (i * (base_radius // (num_arcs + 2)))

            # Dibujar arcos incompletos (estilo huella)
            bbox = [
                center_x - radius,
                center_y - radius,
                center_x + radius,
                center_y + radius
            ]

            # Alternar entre arcos completos y parciales
            if i % 2 == 0:
                # Arco completo
                draw.arc(bbox, 0, 360, fill=primary_color, width=line_width)
            else:
                # Arcos parciales
                draw.arc(bbox, 30, 150, fill=secondary_color, width=line_width)
                draw.arc(bbox, 210, 330, fill=secondary_color, width=line_width)

        # Agregar líneas verticales para simular crestas de huella
        num_lines = size // 12
        line_spacing = (size - margin * 2) // (num_lines + 1)

        for j in range(1, num_lines + 1):
            x = margin + j * line_spacing
            # Líneas onduladas
            y_start = margin + (j % 3) * (size // 20)
            y_end = size - margin - ((j + 1) % 3) * (size // 20)

            # Alternar colores
            color = primary_color if j % 2 == 0 else secondary_color
            draw.line([(x, y_start), (x, y_end)], fill=color, width=line_width)

        # Añadir elipse central (núcleo de la huella)
        core_radius = base_radius // 3
        core_bbox = [
            center_x - core_radius,
            center_y - core_radius,
            center_x + core_radius,
            center_y + core_radius
        ]
        draw.ellipse(core_bbox, outline=primary_color, width=line_width * 2)

        images.append(img)

    # Guardar como .ico con múltiples tamaños
    images[0].save(
        output_path,
        format='ICO',
        sizes=[(img.width, img.height) for img in images],
        append_images=images[1:]
    )

    print(f"✅ Icono creado: {output_path}")
    print(f"   Tamaños incluidos: {sizes}")

    # También guardar una versión PNG grande para referencia
    png_path = output_path.replace('.ico', '.png')
    images[-1].save(png_path, format='PNG')
    print(f"✅ PNG de referencia: {png_path}")

if __name__ == "__main__":
    # Asegurar que existe la carpeta assets
    os.makedirs("assets", exist_ok=True)

    create_fingerprint_icon("assets/fingerprint.ico")
    print("\n🎨 Icono de huella digital creado exitosamente")
