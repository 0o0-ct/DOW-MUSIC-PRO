# config.py
import os
import sys
import shutil
import subprocess

# ============================================================================
# CONFIGURACIÓN GLOBAL
# ============================================================================

VERSION = "4.0 - Professional Edition"
DESARROLLADOR = "Clever JUAREZ - Ing. Sistemas"
FECHA = "Diciembre 2024"

# Configuración de descargas
CARPETA_BASE_DEFECTO = "Descargas"
ORGANIZAR_POR_ARTISTA = True
LIMPIAR_NOMBRE_ARCHIVO = True

# Patrones de URL soportados
PATRONES_URL = [
    'youtube.com/watch?v=',
    'youtube.com/playlist?list=',
    'youtu.be/',
    'music.youtube.com/watch?v=',
    'music.youtube.com/playlist?list='
]

# User Agents rotativos para evitar bloqueos
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15'
]

# Estrategias de descarga
ESTRATEGIAS_DESCARGA = [
    {'nombre': 'Android Music', 'args': {'youtube': {'player_client': ['android_music']}}},
    {'nombre': 'Android', 'args': {'youtube': {'player_client': ['android']}}},
    {'nombre': 'Web', 'args': {'youtube': {'player_client': ['web']}}},
    {'nombre': 'iOS', 'args': {'youtube': {'player_client': ['ios']}}}
]

# Idiomas para subtítulos
IDIOMAS_SUBTITULOS = ['es', 'en', 'es-ES', 'en-US']

# Formatos de audio soportados
FORMATOS_AUDIO = {
    '1': 'mp3', 
    '2': 'flac', 
    '3': 'm4a', 
    '4': 'wav',
    'mp3': 'mp3', 
    'flac': 'flac', 
    'm4a': 'm4a', 
    'wav': 'wav'
}

# ============================================================================
# VERIFICACIÓN DE DEPENDENCIAS
# ============================================================================

def verificar_dependencias():
    """Verifica que todas las dependencias necesarias estén instaladas"""
    dependencias = {
        'yt_dlp': 'yt-dlp',
        'mutagen': 'mutagen',
        'requests': 'requests',
        'PIL': 'Pillow'
    }
    
    faltantes = []
    for modulo, paquete in dependencias.items():
        try:
            __import__(modulo)
        except ImportError:
            faltantes.append(paquete)
            
    if faltantes:
        print("⚠️ Faltan dependencias necesarias:")
        for dep in faltantes:
            print(f"   - {dep}")
        print("\nInstalando dependencias automáticamente...")
        try:
            # Intentar instalar solo si no estamos en un entorno gestionado externamente
            # En Arch Linux esto suele fallar sin venv, pero ejecutar.sh ya maneja el venv
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + faltantes)
            print("✅ Dependencias instaladas correctamente.")
            return True
        except Exception as e:
            print(f"❌ Error instalando dependencias: {e}")
            return False
    return True

def actualizar_herramientas():
    """Intenta actualizar yt-dlp automáticamente"""
    print("🔄 Verificando actualizaciones de yt-dlp...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", "yt-dlp"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ yt-dlp está actualizado.")
    except Exception:
        print("⚠️ No se pudo actualizar yt-dlp (puede que no tengas pip en el PATH)")

def verificar_ffmpeg():
    """Verifica que FFmpeg esté instalado y disponible"""
    if shutil.which("ffmpeg"):
        return True

    # Buscar en la carpeta del script
    try:
        # En caso de script normal
        script_dir = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        # En caso de ejecutable o entorno interactivo
        script_dir = os.getcwd()
        
    local_ffmpeg_path = os.path.join(script_dir, "ffmpeg.exe")
    if os.path.exists(local_ffmpeg_path):
        print("   ✅ ffmpeg.exe encontrado localmente. Añadiendo al PATH...")
        os.environ["PATH"] = script_dir + os.pathsep + os.environ["PATH"]
        return True

    print("❌ FFmpeg no está instalado o no está en el PATH.")
    print("   Es CRÍTICO para la conversión de audio.")
    print("   Descárgalo desde: https://ffmpeg.org/download.html")
    return False
