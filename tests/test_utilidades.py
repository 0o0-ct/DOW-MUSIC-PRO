
import unittest
import sys
import os

# Add parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utilidades import limpiar_nombre_archivo, validar_url_youtube, formatear_duracion, formatear_tamano

class TestUtilidades(unittest.TestCase):

    def test_limpiar_nombre_archivo(self):
        self.assertEqual(limpiar_nombre_archivo("Song / Title"), "Song Title")
        self.assertEqual(limpiar_nombre_archivo("Song: Title"), "Song Title")
        self.assertEqual(limpiar_nombre_archivo("  Song   Title  "), "Song Title")
        self.assertEqual(limpiar_nombre_archivo("Song Title."), "Song Title")
        self.assertEqual(limpiar_nombre_archivo(""), "audio_descargado")

    def test_validar_url_youtube(self):
        self.assertTrue(validar_url_youtube("https://www.youtube.com/watch?v=dQw4w9WgXcQ"))
        self.assertTrue(validar_url_youtube("https://youtu.be/dQw4w9WgXcQ"))
        self.assertTrue(validar_url_youtube("https://music.youtube.com/watch?v=dQw4w9WgXcQ"))
        self.assertFalse(validar_url_youtube("https://www.google.com"))
        self.assertFalse(validar_url_youtube("random text"))
        self.assertFalse(validar_url_youtube(""))

    def test_formatear_duracion(self):
        self.assertEqual(formatear_duracion(65), "1:05")
        self.assertEqual(formatear_duracion(3665), "1:01:05")
        self.assertEqual(formatear_duracion(0), "0:00")
        self.assertEqual(formatear_duracion(None), "??:??")

    def test_formatear_tamano(self):
        self.assertEqual(formatear_tamano(1024), "1.00 KB")
        self.assertEqual(formatear_tamano(1024 * 1024), "1.00 MB")
        self.assertEqual(formatear_tamano(500), "500.00 B")
        self.assertEqual(formatear_tamano(None), "0 B")

if __name__ == '__main__':
    unittest.main()
