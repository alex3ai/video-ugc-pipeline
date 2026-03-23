import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import asyncio

# Adicionando o diretório raiz ao path para permitir imports relativos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.llm_service import LLMService
from services.video_service.video_service import test_video_api_connection
from services.drive_service.drive_service import test_drive_connection


class TestLLMService(unittest.TestCase):
    """Testes para o serviço de LLM (Gemini)"""

    @patch('os.getenv', return_value='fake-api-key')
    def test_llm_service_initialization(self, mock_getenv):
        """Testa se o LLMService pode ser inicializado"""
        # Apenas testa se a inicialização não lança erro com API key fake
        try:
            service = LLMService()
            # Se chegou aqui, a inicialização funcionou
            self.assertIsNotNone(service)
        except Exception as e:
            # Erros de conexao sao esperados sem API key valida
            self.assertIn("API", str(e))


class TestVideoService(unittest.TestCase):
    """Testes para o serviço de vídeo"""

    @patch('requests.get')
    @patch('os.getenv')
    def test_test_video_api_connection_success(self, mock_getenv, mock_requests):
        """Testa a conexão bem-sucedida com a API de vídeo"""
        # Define valores de retorno para os mocks
        mock_getenv.side_effect = [
            'https://api.example.com',  # VIDEO_API_URL
            'fake-api-key'              # VIDEO_API_KEY
        ]
        
        # Simula uma resposta bem-sucedida
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_requests.return_value = mock_response
        
        result = test_video_api_connection()
        self.assertTrue(result)

    @patch('requests.get')
    @patch('os.getenv')
    def test_test_video_api_connection_failure(self, mock_getenv, mock_requests):
        """Testa a falha na conexão com a API de vídeo"""
        # Define valores de retorno para os mocks
        mock_getenv.side_effect = [
            'https://api.example.com',  # VIDEO_API_URL
            'fake-api-key'              # VIDEO_API_KEY
        ]
        
        # Simula uma resposta com falha
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_requests.return_value = mock_response
        
        result = test_video_api_connection()
        self.assertFalse(result)


class TestDriveService(unittest.TestCase):
    """Testes para o serviço do Google Drive"""

    @patch('services.drive_service.drive_service.DriveService')
    def test_test_drive_connection_success(self, mock_drive_service_class):
        """Testa a conexão bem-sucedida com o Google Drive"""
        # Simula uma instância do serviço
        mock_drive_service = MagicMock()
        mock_drive_service.test_connection = MagicMock(return_value=True)
        mock_drive_service_class.return_value = mock_drive_service
        
        result = test_drive_connection()
        self.assertTrue(result)

    @patch('services.drive_service.drive_service.DriveService')
    def test_test_drive_connection_failure(self, mock_drive_service_class):
        """Testa a falha na conexão com o Google Drive"""
        # Simula uma instância do serviço retornando falha
        mock_drive_service = MagicMock()
        mock_drive_service.test_connection = MagicMock(return_value=False)
        mock_drive_service_class.return_value = mock_drive_service
        
        result = test_drive_connection()
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()