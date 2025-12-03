# descargador.py
import os
import time
import yt_dlp
from config import USER_AGENTS, ORGANIZAR_POR_ARTISTA, ESTRATEGIAS_DESCARGA, IDIOMAS_SUBTITULOS
from utilidades import logger, limpiar_nombre_archivo, crear_barra_progreso, formatear_tamano
from metadatos import GestorMetadatos

class Descargador:
    def __init__(self):
        self.gestor_metadatos = GestorMetadatos()

    def _hook_progreso(self, d):
        """Hook para mostrar progreso de descarga"""
        if d['status'] == 'downloading':
            try:
                p = d.get('_percent_str', '0%').replace('%','')
                porcentaje = float(p)
                barra = crear_barra_progreso(porcentaje)
                velocidad = d.get('_speed_str', 'N/A')
                total = d.get('_total_bytes_str', 'N/A')

                print(f"\r[{barra}] {porcentaje:.1f}% | {velocidad} | {total}   ", end='', flush=True)
            except:
                pass
        elif d['status'] == 'finished':
            print("\n✅ Descarga completada. Procesando audio...")

    def descargar(self, url, carpeta_base, formato, opciones):
        """
        Realiza la descarga con múltiples estrategias
        opciones: {letras: bool, thumbnail: bool, es_playlist: bool}
        """
        for estrategia in ESTRATEGIAS_DESCARGA:
            print(f"\n🔧 Probando estrategia: {estrategia['nombre']}")

            try:
                if self._intentar_descarga(url, carpeta_base, formato, opciones, estrategia):
                    return True
            except Exception as e:
                logger.error(f"Fallo en estrategia {estrategia['nombre']}: {e}")
                print(f"❌ Error: {str(e)[:100]}...")
                time.sleep(2)

        return False

    def _intentar_descarga(self, url, carpeta_base, formato, opciones, estrategia):
        """Intenta descargar con una configuración específica"""

        # Configuración de yt-dlp
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': '%(title)s.%(ext)s', # Temporal, se mueve después
            'noplaylist': not opciones.get('es_playlist', False),
            'ignoreerrors': True,
            'writethumbnail': opciones.get('thumbnail', True),
            'writesubtitles': opciones.get('letras', True),
            'subtitleslangs': IDIOMAS_SUBTITULOS,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': formato,
                'preferredquality': '0',
            }],
            'logger': logger,
            'progress_hooks': [self._hook_progreso],
            'extractor_args': estrategia['args'],
            'socket_timeout': 30,
            'retries': 3,
            'fragment_retries': 3,
            # 'quiet': True
        }

        # Manejo seguro de cookies
        cookie_content = None
        try:
            import keyring
            # Intentar recuperar cookies del sistema de claves
            # El servicio se llamaría 'youtube-dl-cookies' y el usuario 'cookies.txt'
            # Esta es una implementación conceptual ya que keyring requiere configuración previa
            stored_cookies = keyring.get_password("youtube-dl-cookies", "cookies_content")
            if stored_cookies:
                # Escribir a un archivo temporal seguro
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', delete=False) as tf:
                    tf.write(stored_cookies)
                    ydl_opts['cookiefile'] = tf.name
                    cookie_content = tf.name
            elif os.path.exists("cookies.txt"):
                 # Fallback a archivo local pero con advertencia en logs
                 logger.warning("Usando cookies.txt local (no seguro)")
                 ydl_opts['cookiefile'] = 'cookies.txt'
        except Exception as e:
            logger.warning(f"Error accediendo al keyring: {e}")
            if os.path.exists("cookies.txt"):
                ydl_opts['cookiefile'] = 'cookies.txt'

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if not info:
                    raise Exception("No se pudo obtener información del video")

                # Preparar lista de items a procesar
                if 'entries' in info:
                    items = list(info['entries'])
                    total = len(items)
                    print(f"📊 Playlist detectada: {total} videos")
                else:
                    items = [info]
                    total = 1

                # Descargar
                error_count = ydl.download([url])

                if error_count > 0 and not opciones.get('es_playlist'):
                    raise Exception("Error en la descarga")

                # Procesar cada archivo descargado
                for idx, item in enumerate(items, 1):
                    if not item: continue
                    self._procesar_archivo(item, carpeta_base, formato, opciones, idx, total)

                return True
        finally:
            # Limpiar archivo temporal de cookies si se creó
            if cookie_content and os.path.exists(cookie_content):
                try: os.remove(cookie_content)
                except: pass

    def _procesar_archivo(self, info, carpeta_base, formato, opciones, idx, total):
        """Procesa el archivo descargado: mueve, renombra y etiqueta"""
        try:
            # Determinar carpeta destino
            carpeta_destino = carpeta_base
            if ORGANIZAR_POR_ARTISTA:
                artista = info.get('artist') or info.get('creator') or 'Varios'
                artista_limpio = limpiar_nombre_archivo(artista)
                carpeta_destino = os.path.join(carpeta_base, artista_limpio)

            if not os.path.exists(carpeta_destino):
                os.makedirs(carpeta_destino)

            # Buscar el archivo descargado (puede estar en el directorio actual)
            titulo = info.get('title', 'audio')
            titulo_limpio = limpiar_nombre_archivo(titulo)

            # yt-dlp descarga en el directorio actual por defecto con nuestra config
            # Buscamos el archivo más reciente que coincida
            archivo_origen = None
            for f in os.listdir('.'):
                if f.endswith(f'.{formato}'):
                    # Heurística simple: si contiene parte del título
                    if titulo_limpio[:15] in limpiar_nombre_archivo(f):
                        archivo_origen = f
                        break

            if not archivo_origen:
                # Intentar buscar por el nombre exacto que yt-dlp usaría
                posible_nombre = f"{info['title']}.{formato}"
                if os.path.exists(posible_nombre):
                    archivo_origen = posible_nombre

            if archivo_origen and os.path.exists(archivo_origen):
                archivo_final = os.path.join(carpeta_destino, f"{titulo_limpio}.{formato}")

                # Implementación de bloqueo de archivos y descarga atómica
                # 1. Usar extensión temporal para el movimiento
                archivo_temporal = archivo_final + ".part"

                # Mover archivo a ubicación temporal
                if os.path.exists(archivo_temporal):
                    os.remove(archivo_temporal)

                # Usar filelock para evitar colisiones
                from filelock import FileLock
                lock_path = archivo_final + ".lock"
                lock = FileLock(lock_path)

                try:
                    with lock.acquire(timeout=10):
                        os.rename(archivo_origen, archivo_temporal)

                        # Procesar metadatos en el archivo temporal
                        meta = self.gestor_metadatos.extraer_metadatos(info, idx, total)

                        img_data = None
                        if opciones.get('thumbnail'):
                            img_url = info.get('thumbnail')
                            img_data = self.gestor_metadatos.descargar_imagen(img_url)

                        letras = ""
                        if opciones.get('letras'):
                            letras = self.gestor_metadatos.obtener_letras(info)

                        self.gestor_metadatos.incrustar_tags(archivo_temporal, formato, meta, img_data, letras)

                        # Renombrar a final solo cuando todo esté listo
                        if os.path.exists(archivo_final):
                            os.remove(archivo_final)
                        os.rename(archivo_temporal, archivo_final)

                        print(f"✅ Procesado: {titulo_limpio}")

                        # Limpiar archivos temporales de imagen si quedaron
                        base_temp = os.path.splitext(archivo_origen)[0]
                        for ext in ['.jpg', '.webp', '.png']:
                            if os.path.exists(base_temp + ext):
                                try: os.remove(base_temp + ext)
                                except: pass

                except Exception as e:
                    logger.error(f"Error en operación atómica de archivo: {e}")
                    # Intentar limpiar temporal si falló
                    if os.path.exists(archivo_temporal):
                        try: os.remove(archivo_temporal)
                        except: pass
                    raise e
                finally:
                     # Limpiar lock file
                     if os.path.exists(lock_path):
                         try: os.remove(lock_path)
                         except: pass

        except Exception as e:
            logger.error(f"Error procesando archivo {info.get('title')}: {e}")
            print(f"⚠️ Error procesando archivo: {e}")
