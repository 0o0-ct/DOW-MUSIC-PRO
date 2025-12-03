# interfaz.py
from config import VERSION, DESARROLLADOR, CARPETA_BASE_DEFECTO, FORMATOS_AUDIO
from utilidades import limpiar_pantalla, preguntar_si_no

def mostrar_banner():
    """Muestra el banner de inicio"""
    print("╔════════════════════════════════════════════╗")
    print("║   YOUTUBE MUSIC DOWNLOADER PRO             ║")
    print(f"║   Versión {VERSION:30s}   ║")
    print("║   Desarrollado por: Clever Juarez          ║")
    print("╚════════════════════════════════════════════╝")
    print()

def mostrar_menu_principal():
    """Muestra el menú principal y retorna la opción seleccionada"""
    print("═══════════════════════════════════════════════")
    print("🎯 MODO DE DESCARGA")
    print("═══════════════════════════════════════════════")
    print()
    print("  1. 🎵 Canción Individual")
    print("     Descarga una canción a la vez")
    print()
    print("2. 📂 Playlist Completa")
    print("     Descarga todas las canciones")
    print()
    print("  3. 📝 Descarga Múltiple")
    print("     Varias canciones por URLs")
    print()
    print("  0. ❌ Salir")
    print("═══════════════════════════════════════════════")

    while True:
        opcion = input("\nSelecciona una opción (0-3): ").strip()
        if opcion in ['0', '1', '2', '3']:
            return opcion
        print("⚠️ Opción inválida. Intenta de nuevo.")

def seleccionar_formato():
    """Permite seleccionar el formato de audio"""
    print("\n🎵 FORMATO DE AUDIO:")
    print("1. MP3 (Máxima Calidad) - Compatible universalmente")
    print("2. FLAC (Lossless) - Máxima calidad sin pérdida")
    print("3. M4A (AAC) - Máxima calidad, menor tamaño")
    print("4. WAV (Lossless PCM) - Calidad de estudio")

    formatos = FORMATOS_AUDIO

    while True:
        opcion = input("\nSelecciona formato (1-4) [Enter = MP3]: ").strip().lower()
        if opcion == '':
            return 'mp3'
        if opcion in formatos:
            return formatos[opcion]
        print("⚠️ Opción inválida. Intenta de nuevo.")

def configurar_opciones():
    """Configura opciones avanzadas"""
    print("\n⚙️ OPCIONES AVANZADAS:")
    
    letras = preguntar_si_no("¿Descargar letras (subtítulos)?")
    thumbnail = preguntar_si_no("¿Descargar carátula?")
    
    return {
        'letras': letras,
        'thumbnail': thumbnail
    }

def solicitar_carpeta(base=CARPETA_BASE_DEFECTO):
    """Solicita la carpeta de destino"""
    carpeta = input(f"📂 Carpeta destino [Enter = {base}]: ").strip()
    return carpeta if carpeta else base
