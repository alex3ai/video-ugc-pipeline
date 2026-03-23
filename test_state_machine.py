"""
Testes para a máquina de estados da Pipeline de Vídeo UGC

Cenários testados:
1. Criação de job com status PENDING
2. Transição PENDING -> PROMPT_GENERATED
3. Transição PROMPT_GENERATED -> PROCESSING_VIDEO
4. Transição PROCESSING_VIDEO -> COMPLETED
5. Transição PROCESSING_VIDEO -> FAILED
6. Transição PROCESSING_VIDEO -> TIMEOUT
7. Retry com HTTP 503 (Cold Start)
8. Fluxo completo da máquina de estados
"""
import unittest
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime, timezone
import sys
import os

# Adicionando o diretório raiz ao path para permitir imports relativos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.entities import JobStatusEnum, PipelineJob, Campaign


class TestStateMachineScenarios(unittest.TestCase):
    """Testes para a máquina de estados completa com diferentes cenários"""

    def setUp(self):
        """Configuração inicial para os testes"""
        # Mock do banco de dados
        self.mock_db = Mock(spec=['query', 'add', 'commit', 'refresh'])
        
        # Mock da campanha
        self.mock_campaign = Mock(spec=Campaign)
        self.mock_campaign.id = 1
        self.mock_campaign.name = "Test Campaign"
        self.mock_campaign.briefing_text = "This is a valid briefing text with more than fifty characters."
        
        # Mock do job
        self.mock_job = Mock(spec=PipelineJob)
        self.mock_job.id = 1
        self.mock_job.campaign_id = 1
        self.mock_job.status = JobStatusEnum.PENDING
        self.mock_job.prompt = None
        self.mock_job.video_url = None
        self.mock_job.error_message = None

    def test_job_status_enum_has_all_states(self):
        """Testa se o enum JobStatusEnum tem todos os estados necessários"""
        self.assertEqual(JobStatusEnum.PENDING.value, "PENDING")
        self.assertEqual(JobStatusEnum.PROMPT_GENERATED.value, "PROMPT_GENERATED")
        self.assertEqual(JobStatusEnum.PROCESSING_VIDEO.value, "PROCESSING_VIDEO")
        self.assertEqual(JobStatusEnum.COMPLETED.value, "COMPLETED")
        self.assertEqual(JobStatusEnum.FAILED.value, "FAILED")
        self.assertEqual(JobStatusEnum.TIMEOUT.value, "TIMEOUT")

    def test_send_prompt_to_video_api_success(self):
        """Testa envio do prompt para API de vídeo com sucesso (200/202)"""
        from services.job_service.job_service import send_prompt_to_video_api
        
        self.mock_job.status = JobStatusEnum.PROMPT_GENERATED
        self.mock_job.prompt = "Test prompt"
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.mock_job
        
        with patch('services.job_service.job_service.settings') as mock_settings:
            mock_settings.VIDEO_API_URL = "https://api.example.com"
            mock_settings.VIDEO_API_KEY = "test-key"
            mock_settings.MAX_RETRIES = 3
            mock_settings.REQUEST_TIMEOUT = 30
            
            with patch('requests.post') as mock_post:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_post.return_value = mock_response
                
                result = send_prompt_to_video_api(self.mock_db, 1)
                
                self.assertTrue(result)
                mock_post.assert_called_once()

    def test_send_prompt_to_video_api_wrong_status(self):
        """Testa que send_prompt_to_video_api falha se status não for PROMPT_GENERATED"""
        from services.job_service.job_service import send_prompt_to_video_api
        
        self.mock_job.status = JobStatusEnum.PENDING  # Status errado
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.mock_job
        
        result = send_prompt_to_video_api(self.mock_db, 1)
        
        self.assertFalse(result)

    def test_send_prompt_to_video_api_503_retry(self):
        """Testa retry com HTTP 503 (Cold Start) - retry e sucesso"""
        from services.job_service.job_service import send_prompt_to_video_api
        
        self.mock_job.status = JobStatusEnum.PROMPT_GENERATED
        self.mock_job.prompt = "Test prompt"
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.mock_job
        
        with patch('services.job_service.job_service.settings') as mock_settings:
            mock_settings.VIDEO_API_URL = "https://api.example.com"
            mock_settings.VIDEO_API_KEY = "test-key"
            mock_settings.MAX_RETRIES = 3
            mock_settings.REQUEST_TIMEOUT = 30
            
            with patch('requests.post') as mock_post:
                # Primeira chamada retorna 503, segunda retorna 200
                mock_503 = Mock()
                mock_503.status_code = 503
                mock_200 = Mock()
                mock_200.status_code = 200
                mock_post.side_effect = [mock_503, mock_200]
                
                with patch('time.sleep'):  # Não esperar de verdade
                    result = send_prompt_to_video_api(self.mock_db, 1)
                    
                    self.assertTrue(result)
                    self.assertEqual(mock_post.call_count, 2)

    def test_send_prompt_to_video_api_503_exhaust_retries(self):
        """Testa falha após exaurir retries de HTTP 503"""
        from services.job_service.job_service import send_prompt_to_video_api
        
        self.mock_job.status = JobStatusEnum.PROMPT_GENERATED
        self.mock_job.prompt = "Test prompt"
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.mock_job
        
        with patch('services.job_service.job_service.settings') as mock_settings:
            mock_settings.VIDEO_API_URL = "https://api.example.com"
            mock_settings.VIDEO_API_KEY = "test-key"
            mock_settings.MAX_RETRIES = 3
            mock_settings.REQUEST_TIMEOUT = 30
            
            with patch('requests.post') as mock_post:
                # Sempre retorna 503
                mock_503 = Mock()
                mock_503.status_code = 503
                mock_post.return_value = mock_503
                
                with patch('time.sleep'):
                    with patch('services.job_service.job_service.update_job_status') as mock_update:
                        result = send_prompt_to_video_api(self.mock_db, 1)
                        
                        # Falhou após 3 retries
                        self.assertFalse(result)
                        self.assertEqual(mock_post.call_count, 3)
                        # Verificar se update_job_status foi chamado com FAILED
                        mock_update.assert_called()

    def test_send_prompt_to_video_api_http_error(self):
        """Testa que send_prompt_to_video_api atualiza para FAILED em caso de erro HTTP"""
        from services.job_service.job_service import send_prompt_to_video_api
        
        self.mock_job.status = JobStatusEnum.PROMPT_GENERATED
        self.mock_job.prompt = "Test prompt"
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.mock_job
        
        with patch('services.job_service.job_service.settings') as mock_settings:
            mock_settings.VIDEO_API_URL = "https://api.example.com"
            mock_settings.VIDEO_API_KEY = "test-key"
            mock_settings.MAX_RETRIES = 1
            mock_settings.REQUEST_TIMEOUT = 30
            
            with patch('requests.post') as mock_post:
                mock_response = Mock()
                mock_response.status_code = 500
                mock_response.text = "Internal Server Error"
                mock_post.return_value = mock_response
                
                with patch('services.job_service.job_service.update_job_status') as mock_update:
                    result = send_prompt_to_video_api(self.mock_db, 1)
                    
                    self.assertFalse(result)
                    # Verificar se update_job_status foi chamado com FAILED
                    mock_update.assert_called()

    def test_poll_video_status_completed(self):
        """Testa polling quando vídeo está COMPLETED"""
        from services.job_service.job_service import poll_video_processing_status
        
        self.mock_job.status = JobStatusEnum.PROCESSING_VIDEO
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.mock_job
        
        with patch('services.job_service.job_service.settings') as mock_settings:
            mock_settings.VIDEO_API_URL = "https://api.example.com"
            mock_settings.VIDEO_API_KEY = "test-key"
            mock_settings.REQUEST_TIMEOUT = 30
            
            with patch('requests.get') as mock_get:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "status": "completed",
                    "video_url": "https://example.com/video.mp4"
                }
                mock_get.return_value = mock_response
                
                result = poll_video_processing_status(self.mock_db, 1)
                
                self.assertTrue(result)

    def test_poll_video_status_failed(self):
        """Testa polling quando vídeo FAILED"""
        from services.job_service.job_service import poll_video_processing_status
        
        self.mock_job.status = JobStatusEnum.PROCESSING_VIDEO
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.mock_job
        
        with patch('services.job_service.job_service.settings') as mock_settings:
            mock_settings.VIDEO_API_URL = "https://api.example.com"
            mock_settings.VIDEO_API_KEY = "test-key"
            mock_settings.REQUEST_TIMEOUT = 30
            
            with patch('requests.get') as mock_get:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "status": "failed",
                    "error": "Render failed"
                }
                mock_get.return_value = mock_response
                
                result = poll_video_processing_status(self.mock_db, 1)
                
                self.assertTrue(result)  # Retorna True porque processamento terminou

    def test_poll_video_status_timeout(self):
        """Testa polling quando atinge TIMEOUT"""
        from services.job_service.job_service import poll_video_processing_status
        
        self.mock_job.status = JobStatusEnum.PROCESSING_VIDEO
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.mock_job
        
        with patch('services.job_service.job_service.settings') as mock_settings:
            mock_settings.VIDEO_API_URL = "https://api.example.com"
            mock_settings.VIDEO_API_KEY = "test-key"
            mock_settings.REQUEST_TIMEOUT = 5
            
            with patch('requests.get') as mock_get:
                # Sempre retorna "processing"
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"status": "processing"}
                mock_get.return_value = mock_response
                
                with patch('time.time') as mock_time:
                    # Simular passagem de tempo > 600s (timeout)
                    mock_time.side_effect = [0, 601]
                    
                    with patch('time.sleep'):
                        with patch('services.job_service.job_service.update_job_status') as mock_update:
                            result = poll_video_processing_status(self.mock_db, 1)
                            
                            # Retorna True porque atingiu timeout
                            self.assertTrue(result)
                            # Verificar se update_job_status foi chamado com TIMEOUT
                            mock_update.assert_called()

    def test_transition_job_status_pending_to_prompt_generated_success(self):
        """Testa transição de status PENDING -> PROMPT_GENERATED com sucesso"""
        from services.job_service.job_service import transition_job_status_pending_to_prompt_generated
        
        self.mock_job.status = JobStatusEnum.PENDING
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.mock_job
        
        with patch('services.job_service.job_service.update_job_status') as mock_update:
            result = transition_job_status_pending_to_prompt_generated(
                self.mock_db, 1, "Generated prompt"
            )
            
            self.assertTrue(result)
            mock_update.assert_called_once()

    def test_transition_job_status_wrong_status(self):
        """Testa que transição falha se status não for PENDING"""
        from services.job_service.job_service import transition_job_status_pending_to_prompt_generated
        
        # Job já está em outro status
        self.mock_job.status = JobStatusEnum.PROMPT_GENERATED
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.mock_job
        
        result = transition_job_status_pending_to_prompt_generated(
            self.mock_db, 1, "Generated prompt"
        )
        
        self.assertFalse(result)

    def test_state_machine_full_flow(self):
        """Testa o fluxo completo: PENDING -> PROMPT_GENERATED -> PROCESSING_VIDEO -> COMPLETED"""
        from services.job_service.job_service import (
            transition_job_status_pending_to_prompt_generated,
            send_prompt_to_video_api,
            poll_video_processing_status
        )
        
        # 1. Job começa em PENDING
        self.mock_job.status = JobStatusEnum.PENDING
        self.mock_job.prompt = "Generated prompt"
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.mock_job
        
        # 2. Transição PENDING -> PROMPT_GENERATED
        with patch('services.job_service.job_service.update_job_status'):
            result = transition_job_status_pending_to_prompt_generated(
                self.mock_db, 1, "Generated prompt"
            )
            self.assertTrue(result)
        
        # 3. Atualiza status para PROMPT_GENERATED
        self.mock_job.status = JobStatusEnum.PROMPT_GENERATED
        
        # 4. Envio para API de vídeo
        with patch('services.job_service.job_service.settings') as mock_settings:
            mock_settings.VIDEO_API_URL = "https://api.example.com"
            mock_settings.VIDEO_API_KEY = "test-key"
            mock_settings.MAX_RETRIES = 3
            mock_settings.REQUEST_TIMEOUT = 30
            
            with patch('requests.post') as mock_post:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_post.return_value = mock_response
                
                result = send_prompt_to_video_api(self.mock_db, 1)
                self.assertTrue(result)
        
        # 5. Atualiza status para PROCESSING_VIDEO
        self.mock_job.status = JobStatusEnum.PROCESSING_VIDEO
        
        # 6. Polling até COMPLETED
        with patch('services.job_service.job_service.settings') as mock_settings:
            mock_settings.VIDEO_API_URL = "https://api.example.com"
            mock_settings.VIDEO_API_KEY = "test-key"
            mock_settings.REQUEST_TIMEOUT = 30
            
            with patch('requests.get') as mock_get:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "status": "completed",
                    "video_url": "https://example.com/video.mp4"
                }
                mock_get.return_value = mock_response
                
                result = poll_video_processing_status(self.mock_db, 1)
                self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
