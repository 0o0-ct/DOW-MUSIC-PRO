# instalar.py
import os
import sys
import subprocess
import shutil

def main():
    print("╔════════════════════════════════════════════╗")
    print("║   INSTALADOR - YOUTUBE MUSIC DOWNLOADER    ║")
    print("╚════════════════════════════════════════════╝")
    print()

    # 1. Verificar Python
    print(f"✅ Python detectado: {sys.version.split()[0]}")
    if sys.version_info < (3, 7):
        print("❌ Se requiere Python 3.7 o superior")
        return

    # 2. Actualizar pip
    print("\n🔄 Actualizando pip...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    except:
        print("⚠️ No se pudo actualizar pip, continuando...")

    # 3. Instalar dependencias
    print("\n📦 Instalando dependencias...")
    requirements = ['yt-dlp', 'mutagen', 'requests', 'Pillow']
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + requirements)
        print("✅ Dependencias instaladas")
    except Exception as e:
        print(f"❌ Error instalando dependencias: {e}")
        return

    # 4. Verificar FFmpeg
    print("\n🎥 Verificando FFmpeg...")
    if shutil.which("ffmpeg"):
        print("✅ FFmpeg encontrado en el sistema")
    else:
        print("⚠️ FFmpeg no encontrado en el PATH")
        print("   Buscando ffmpeg.exe local...")
        if os.path.exists("ffmpeg.exe"):
            print("✅ ffmpeg.exe encontrado localmente")
        else:
            print("❌ FFmpeg no encontrado. Es necesario para convertir audio.")
            print("   Descarga ffmpeg.exe y colócalo en esta carpeta.")

    # 5. Crear carpetas
    print("\n📂 Creando estructura de carpetas...")
    os.makedirs("Descargas", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    print("✅ Carpetas listas")

    print("\n✨ ¡Instalación completada!")
    print("   Ejecuta 'Ejecutar.bat' (Windows) o 'python Principal.py' para iniciar.")
    input("\nPresiona Enter para salir...")

if __name__ == "__main__":
    main()
