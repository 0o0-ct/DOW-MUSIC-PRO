
import unittest
from unittest.mock import MagicMock, patch
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from metadatos import GestorMetadatos

class TestGestorMetadatos(unittest.TestCase):

    def setUp(self):
        self.gestor = GestorMetadatos()

    @patch('requests.get')
    def test_descargar_imagen(self, mock_get):
        # Configurar mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'fake_image_data'
        mock_get.return_value = mock_response

        # Test
        data = self.gestor.descargar_imagen('http://example.com/image.jpg')
        self.assertEqual(data, b'fake_image_data')
        # Verificar que se cacheó
        self.assertEqual(self.gestor.cache_imagenes['http://example.com/image.jpg'], b'fake_image_data')

    def test_extraer_metadatos(self):
        entry = {
            'title': 'My Song',
            'artist': 'My Artist',
            'album': 'My Album',
            'upload_date': '20230101'
        }
        meta = self.gestor.extraer_metadatos(entry, 1, 10)
        self.assertEqual(meta['title'], 'My Song')
        self.assertEqual(meta['artist'], 'My Artist')
        self.assertEqual(meta['album'], 'My Album')
        self.assertEqual(meta['year'], '2023')
        self.assertEqual(meta['track'], '1/10')

    @patch('requests.get')
    def test_obtener_letras(self, mock_get):
        info = {
            'requested_subtitles': {
                'es': {'url': 'http://example.com/subs'}
            }
        }
        mock_response = MagicMock()
        mock_response.text = 'La la la'
        mock_get.return_value = mock_response

        letras = self.gestor.obtener_letras(info)
        self.assertEqual(letras, 'La la la')

if __name__ == '__main__':
    unittest.main()
