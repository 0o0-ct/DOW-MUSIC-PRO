# metadatos.py
import os
import requests
from mutagen.flac import FLAC, Picture
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, USLT, TIT2, TPE1, TALB, TDRC, TCON, TRCK
from mutagen.mp4 import MP4, MP4Cover
from config import IDIOMAS_SUBTITULOS
from utilidades import logger, convertir_webp_a_jpeg, limpiar_html

class GestorMetadatos:
    def __init__(self):
        self.cache_imagenes = {}

    def descargar_imagen(self, url):
        """Descarga una imagen y la guarda en caché"""
        if not url:
            return None
            
        if url in self.cache_imagenes:
            return self.cache_imagenes[url]
            
        try:
            logger.info(f"Descargando carátula: {url}")
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                data = response.content
                # Convertir si es necesario
                if b"RIFF" in data[:4] or b"WEBP" in data[:20]:
                    data = convertir_webp_a_jpeg(data)
                
                self.cache_imagenes[url] = data
                return data
        except Exception as e:
            logger.error(f"Error descargando imagen: {e}")
            
        return None

    def extraer_metadatos(self, entry, idx=1, total=1):
        """Extrae metadatos normalizados de la información de yt-dlp"""
        meta = {}
        meta['title'] = entry.get('title', 'Sin título')
        
        # Prioridad de artista
        meta['artist'] = (
            entry.get('artist') or 
            entry.get('creator') or 
            entry.get('uploader') or 
            entry.get('channel') or 
            'Desconocido'
        )
        
        meta['album'] = entry.get('album') or entry.get('playlist_title') or entry.get('title')
        
        fecha = entry.get('release_date') or entry.get('upload_date')
        meta['year'] = str(fecha)[:4] if fecha and len(str(fecha)) >= 4 else None
        
        meta['genre'] = entry.get('genre') or 'Music'
        meta['track'] = f"{idx}/{total}" if total > 1 else str(idx)
        
        return meta

    def obtener_letras(self, info):
        """Obtiene letras si están disponibles"""
        if not info.get('requested_subtitles'):
            return ""
            
        for lang in IDIOMAS_SUBTITULOS:
            if lang in info['requested_subtitles']:
                sub_info = info['requested_subtitles'][lang]
                if 'url' in sub_info:
                    try:
                        content = requests.get(sub_info['url'], timeout=10).text
                        return limpiar_html(content)
                    except Exception as e:
                        logger.error(f"Error obteniendo letras: {e}")
        return ""

    def incrustar_tags(self, archivo, formato, meta, img_data, letras):
        """Incrusta metadatos en el archivo de audio"""
        try:
            logger.info(f"Incrustando metadatos en {os.path.basename(archivo)}")
            
            if formato == 'mp3':
                self._incrustar_mp3(archivo, meta, img_data, letras)
            elif formato == 'flac':
                self._incrustar_flac(archivo, meta, img_data, letras)
            elif formato == 'm4a':
                self._incrustar_m4a(archivo, meta, img_data, letras)
                
            return True
        except Exception as e:
            logger.error(f"Error incrustando metadatos: {e}")
            return False

    def _incrustar_mp3(self, archivo, meta, img_data, letras):
        audio = MP3(archivo, ID3=ID3)
        try:
            audio.add_tags()
        except:
            pass

        if img_data:
            audio.tags.delall("APIC")
            audio.tags.add(APIC(
                encoding=3,
                mime='image/jpeg',
                type=3,
                desc='Cover',
                data=img_data
            ))

        if meta.get('title'): audio.tags.add(TIT2(encoding=3, text=meta['title']))
        if meta.get('artist'): audio.tags.add(TPE1(encoding=3, text=meta['artist']))
        if meta.get('album'): audio.tags.add(TALB(encoding=3, text=meta['album']))
        if meta.get('year'): audio.tags.add(TDRC(encoding=3, text=meta['year']))
        if meta.get('genre'): audio.tags.add(TCON(encoding=3, text=meta['genre']))
        if meta.get('track'): audio.tags.add(TRCK(encoding=3, text=meta['track']))
        if letras: audio.tags.add(USLT(encoding=3, lang='eng', desc='', text=letras))

        audio.save(v2_version=3)

    def _incrustar_flac(self, archivo, meta, img_data, letras):
        audio = FLAC(archivo)
        
        if img_data:
            audio.clear_pictures()
            pic = Picture()
            pic.data = img_data
            pic.type = 3
            pic.mime = "image/jpeg"
            pic.desc = "Cover"
            audio.add_picture(pic)

        if meta.get('title'): audio['TITLE'] = meta['title']
        if meta.get('artist'): audio['ARTIST'] = meta['artist']
        if meta.get('album'): audio['ALBUM'] = meta['album']
        if meta.get('year'): audio['DATE'] = meta['year']
        if meta.get('genre'): audio['GENRE'] = meta['genre']
        if meta.get('track'): audio['TRACKNUMBER'] = meta['track']
        if letras: audio['LYRICS'] = letras

        audio.save()

    def _incrustar_m4a(self, archivo, meta, img_data, letras):
        audio = MP4(archivo)
        
        if img_data:
            audio.tags['covr'] = [MP4Cover(img_data, imageformat=MP4Cover.FORMAT_JPEG)]

        if meta.get('title'): audio.tags['©nam'] = meta['title']
        if meta.get('artist'): audio.tags['©ART'] = meta['artist']
        if meta.get('album'): audio.tags['©alb'] = meta['album']
        if meta.get('year'): audio.tags['©day'] = meta['year']
        if meta.get('genre'): audio.tags['©gen'] = meta['genre']
        if letras: audio.tags['©lyr'] = letras

        audio.save()
