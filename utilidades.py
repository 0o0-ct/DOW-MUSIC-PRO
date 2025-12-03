# utilidades.py
import os
import re
import html
import time
import logging
from datetime import datetime
from io import BytesIO

# Configuración de logging
if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('DOW-Pro')

def limpiar_pantalla():
    """Limpia la pantalla de la consola"""
    os.system('cls' if os.name == 'nt' else 'clear')

def limpiar_nombre_archivo(nombre):
    """Elimina caracteres ilegales para el sistema de archivos"""
    # Eliminar caracteres inválidos en Windows/Linux
    nombre = re.sub(r'[/\\:*?"<>|]+', '', nombre).strip()
    # Eliminar puntos al inicio o final
    nombre = nombre.strip('.')
    # Normalizar espacios múltiples
    nombre = re.sub(r'\s+', ' ', nombre)
    # Limitar longitud
    if len(nombre) > 200:
        nombre = nombre[:200]
    # Fallback si queda vacío
    if not nombre:
        nombre = "audio_descargado"
    return nombre

def convertir_webp_a_jpeg(data):
    """Convierte imágenes WebP/RIFF a JPEG para compatibilidad"""
    try:
        from PIL import Image
        
        # Detectar si es WebP o RIFF
        if data[:4] == b'RIFF' and data[8:12] == b'WEBP':
            pass # Es WebP
        
        img = Image.open(BytesIO(data))
        
        # Convertir a RGB (eliminar canal alpha si existe)
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            bg = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            bg.paste(img, mask=img.split()[3])
            img = bg
        else:
            img = img.convert('RGB')
            
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=95, optimize=True)
        return buffer.getvalue()
    except Exception as e:
        logger.error(f"Error convirtiendo imagen: {e}")
        return data

def limpiar_html(texto):
    """Limpia texto de subtítulos/letras"""
    if not texto:
        return ""
    
    try:
        texto = html.unescape(texto)
        # Eliminar tags HTML
        texto = re.sub(r'<[^>]+>', '', texto)
        # Eliminar timestamps de VTT/SRT
        texto = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}\.\d{3}', '', texto)
        # Eliminar números de línea solos
        texto = re.sub(r'^\d+$', '', texto, flags=re.MULTILINE)
        # Eliminar cabeceras VTT
        texto = re.sub(r'WEBVTT.*?Kind:.*?Language:.*?\n', '', texto, flags=re.IGNORECASE)
        # Normalizar saltos de línea
        texto = re.sub(r'\n\s*\n', '\n\n', texto)
        return texto.strip()
    except Exception as e:
        logger.error(f"Error limpiando HTML: {e}")
        return texto

def formatear_duracion(segundos):
    """Convierte segundos a formato H:MM:SS"""
    if segundos is None:
        return "??:??"
    try:
        segundos = int(segundos)
        h = segundos // 3600
        m = (segundos % 3600) // 60
        s = segundos % 60
        if h > 0:
            return f"{h}:{m:02d}:{s:02d}"
        return f"{m}:{s:02d}"
    except:
        return "??:??"

def formatear_tamano(bytes_size):
    """Convierte bytes a formato legible (MB, GB)"""
    if not bytes_size:
        return "0 B"
    try:
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
    except:
        return "N/A"

def crear_barra_progreso(porcentaje, longitud=30):
    """Crea una barra de progreso visual"""
    try:
        porcentaje = max(0, min(100, float(porcentaje)))
        llenos = int(longitud * porcentaje / 100)
        vacios = longitud - llenos
        barra = "█" * llenos + "░" * vacios
        return barra
    except:
        return "░" * longitud

def validar_url_youtube(url):
    """Valida si una URL parece ser de YouTube"""
    if not url:
        return False
    patrones = [
        r'youtube\.com/watch\?v=',
        r'youtu\.be/',
        r'youtube\.com/playlist\?list=',
        r'music\.youtube\.com'
    ]
    return any(re.search(p, url) for p in patrones)

def preguntar_si_no(pregunta):
    """Realiza una pregunta de sí/no al usuario"""
    while True:
        respuesta = input(f"{pregunta} (s/n): ").strip().lower()
        if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
            return True
        elif respuesta in ['n', 'no']:
            return False
        print("⚠️ Por favor responde 's' o 'n'")

def mostrar_estadisticas(exitosas, fallidas, tiempo_inicio):
    """Muestra estadísticas finales de la sesión"""
    tiempo_total = time.time() - tiempo_inicio
    total = exitosas + fallidas
    tasa_exito = (exitosas / total * 100) if total > 0 else 0
    
    print("\n" + "═"*39)
    print("📊 ESTADÍSTICAS DE DESCARGA")
    print("═"*39)
    print(f"✅ Exitosas:      {exitosas}")
    print(f"❌ Fallidas:      {fallidas}")
    print(f"📁 Total:         {total}")
    print(f"⏱️ Tiempo total:  {formatear_duracion(tiempo_total)}")
    print(f"📈 Tasa de éxito: {tasa_exito:.1f}%")
    print("═"*39)
