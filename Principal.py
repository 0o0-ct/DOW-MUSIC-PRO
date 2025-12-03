# Principal.py
import time
import traceback
from config import verificar_dependencias, actualizar_herramientas, verificar_ffmpeg
from utilidades import (limpiar_pantalla, mostrar_estadisticas, preguntar_si_no,
                       validar_url_youtube)
from interfaz import (mostrar_banner, mostrar_menu_principal, seleccionar_formato,
                     configurar_opciones, solicitar_carpeta)
from descargador import Descargador

def main():
    try:
        limpiar_pantalla()
        mostrar_banner()

        # Verificaciones iniciales
        if not verificar_dependencias():
            input("Presiona Enter para salir...")
            return

        actualizar_herramientas()

        if not verificar_ffmpeg():
            input("Presiona Enter para salir...")
            return

        print("✅ Todas las dependencias están listas\n")
        time.sleep(1)

        descargador = Descargador()

        while True:
            limpiar_pantalla()
            mostrar_banner()
            opcion = mostrar_menu_principal()

            if opcion == '0':
                print("\n👋 ¡Gracias por usar YouTube Music Downloader Pro!")
                break

            # Configuración común para todos los modos
            formato = seleccionar_formato()
            opciones = configurar_opciones()
            carpeta = solicitar_carpeta()

            # Estadísticas de sesión
            exitosas = 0
            fallidas = 0
            tiempo_inicio = time.time()

            if opcion == '1': # Individual
                while True:
                    url = input("\n🔗 URL de YouTube: ").strip()
                    if not url: break

                    if not validar_url_youtube(url):
                        print("⚠️ URL inválida. Por favor ingresa un enlace de YouTube válido.")
                        continue

                    opciones['es_playlist'] = False
                    if descargador.descargar(url, carpeta, formato, opciones):
                        exitosas += 1
                    else:
                        fallidas += 1

                    if not preguntar_si_no("\n¿Descargar otra canción?"):
                        break

            elif opcion == '2': # Playlist
                url = input("\n🔗 URL de Playlist: ").strip()
                if url:
                    if not validar_url_youtube(url):
                        print("⚠️ URL inválida. Por favor ingresa un enlace de YouTube válido.")
                    else:
                        opciones['es_playlist'] = True
                        if descargador.descargar(url, carpeta, formato, opciones):
                            exitosas += 1 # Cuenta como 1 operación exitosa (aunque sean muchos videos)
                        else:
                            fallidas += 1

            elif opcion == '3': # Múltiple
                print("\nIngresa las URLs una por una (deja vacío para terminar)")
                urls = []
                while True:
                    url = input(f"URL #{len(urls) + 1}: ").strip()
                    if not url: break

                    if not validar_url_youtube(url):
                        print("⚠️ URL inválida. Se omitirá.")
                        continue

                    urls.append(url)

                opciones['es_playlist'] = False
                for i, url in enumerate(urls, 1):
                    print(f"\nProcesando {i}/{len(urls)}")
                    if descargador.descargar(url, carpeta, formato, opciones):
                        exitosas += 1
                    else:
                        fallidas += 1

            mostrar_estadisticas(exitosas, fallidas, tiempo_inicio)
            input("\nPresiona Enter para volver al menú...")

    except KeyboardInterrupt:
        print("\n\n⚠️ Programa interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error crítico: {e}")
        traceback.print_exc()
        input("Presiona Enter para salir...")

if __name__ == "__main__":
    main()
