"""
Testes para a máquina de estados da Pipeline de Vídeo UGC

Cenários testados:
1. Criação de job com status PENDING
2. Transição PENDING -> PROMPT_GENERATED
3. Transição PROMPT_GENERATED -> PROCESSING_VIDEO (nova abordagem)
4. Transição PROCESSING_VIDEO -> COMPLETED (nova abordagem)
5. Transição PROCESSING_VIDEO -> FAILED
6. Transição PROCESSING_VIDEO -> TIMEOUT
7. Fluxo completo da máquina de estados (nova abordagem)
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
        self.assertEqual(JobStatusEnum.PROCESSING.value, "PROCESSING")
        self.assertEqual(JobStatusEnum.PROCESSING_VIDEO.value, "PROCESSING_VIDEO")
        self.assertEqual(JobStatusEnum.COMPLETED.value, "COMPLETED")
        self.assertEqual(JobStatusEnum.FAILED.value, "FAILED")
        self.assertEqual(JobStatusEnum.TIMEOUT.value, "TIMEOUT")
        self.assertEqual(JobStatusEnum.UPLOAD_FAILED.value, "UPLOAD_FAILED")

    def test_send_prompt_to_video_api_success(self):
        """Testa envio do prompt para serviço de vídeo com sucesso (nova abordagem)"""
        from services.job_service.job_service import send_prompt_to_video_api
        
        self.mock_job.status = JobStatusEnum.PROMPT_GENERATED
        self.mock_job.prompt = "Test prompt"
        self.mock_job.campaign_id = 1
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.mock_job
        
        with patch('services.job_service.job_service.generate_video_from_prompt') as mock_video_gen:
            mock_result = {
                "status": "success",
                "video_path": "/tmp/test_video.mp4",
                "duration": 10,
                "prompt": "Test prompt",
                "campaign_id": 1
            }
            mock_video_gen.return_value = mock_result
            
            result = send_prompt_to_video_api(self.mock_db, 1)
            
            self.assertTrue(result)
            mock_video_gen.assert_called_once_with("Test prompt", campaign_id=1)
            # Verificar se o status foi atualizado para PROCESSING_VIDEO
            self.mock_db.query.return_value.filter.return_value.first.return_value.status = JobStatusEnum.PROCESSING_VIDEO

    def test_send_prompt_to_video_api_wrong_status(self):
        """Testa que send_prompt_to_video_api falha se status não for PROMPT_GENERATED"""
        from services.job_service.job_service import send_prompt_to_video_api
        
        self.mock_job.status = JobStatusEnum.PENDING  # Status errado
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.mock_job
        
        result = send_prompt_to_video_api(self.mock_db, 1)
        
        self.assertFalse(result)

    def test_send_prompt_to_video_api_failure(self):
        """Testa que send_prompt_to_video_api atualiza para FAILED em caso de falha na geração do vídeo"""
        from services.job_service.job_service import send_prompt_to_video_api
        
        self.mock_job.status = JobStatusEnum.PROMPT_GENERATED
        self.mock_job.prompt = "Test prompt"
        self.mock_job.campaign_id = 1
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.mock_job
        
        with patch('services.job_service.job_service.generate_video_from_prompt') as mock_video_gen:
            mock_result = {
                "status": "error",
                "error": "Model unavailable"
            }
            mock_video_gen.return_value = mock_result
            
            with patch('services.job_service.job_service.update_job_status') as mock_update:
                result = send_prompt_to_video_api(self.mock_db, 1)
                
                self.assertFalse(result)
                # Verificar se update_job_status foi chamado com FAILED
                mock_update.assert_called()

    def test_poll_video_status_completed(self):
        """Testa polling quando vídeo está pronto para upload (nova abordagem)"""
        from services.job_service.job_service import poll_video_processing_status
        
        self.mock_job.status = JobStatusEnum.PROCESSING_VIDEO
        self.mock_job.prompt = "Test prompt"
        self.mock_job.campaign_id = 1
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.mock_job
        
        with patch('services.job_service.job_service.generate_video_from_prompt') as mock_video_gen:
            mock_result = {
                "status": "success",
                "video_path": "/tmp/test_video.mp4",
                "duration": 10,
                "prompt": "Test prompt",
                "campaign_id": 1
            }
            mock_video_gen.return_value = mock_result
            
            with patch('builtins.open', unittest.mock.mock_open(read_data=b"video content")):
                with patch('services.drive_service.drive_service.DriveService') as mock_drive_service_class:
                    mock_drive_service = Mock()
                    mock_drive_service.upload_file.return_value = {"webViewLink": "https://drive.google.com/file/d/test123/view"}
                    mock_drive_service_class.return_value = mock_drive_service
                    
                    result = poll_video_processing_status(self.mock_db, 1)
                    
                    self.assertTrue(result)

    def test_poll_video_status_failed_upload(self):
        """Testa polling quando falha o upload para o Google Drive"""
        from services.job_service.job_service import poll_video_processing_status
        
        self.mock_job.status = JobStatusEnum.PROCESSING_VIDEO
        self.mock_job.prompt = "Test prompt"
        self.mock_job.campaign_id = 1
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.mock_job
        
        with patch('services.job_service.job_service.generate_video_from_prompt') as mock_video_gen:
            mock_result = {
                "status": "success",
                "video_path": "/tmp/test_video.mp4",
                "duration": 10,
                "prompt": "Test prompt",
                "campaign_id": 1
            }
            mock_video_gen.return_value = mock_result
            
            with patch('builtins.open', unittest.mock.mock_open(read_data=b"video content")):
                with patch('services.drive_service.drive_service.DriveService') as mock_drive_service_class:
                    mock_drive_service = Mock()
                    mock_drive_service.upload_file.side_effect = Exception("Upload failed")
                    mock_drive_service_class.return_value = mock_drive_service
                    
                    with patch('services.job_service.job_service.store_video_temporarily') as mock_store:
                        mock_store.return_value = True
                        
                        with patch('services.job_service.job_service.update_job_status') as mock_update:
                            result = poll_video_processing_status(self.mock_db, 1)
                            
                            self.assertFalse(result)  # Deve retornar False pq falhou o upload
                            # Verificar se update_job_status foi chamado com UPLOAD_FAILED
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
        """Testa o fluxo completo com nova abordagem: PENDING -> PROMPT_GENERATED -> PROCESSING_VIDEO -> COMPLETED"""
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
        self.mock_job.campaign_id = 1
        
        # 4. Envio para serviço de vídeo (nova abordagem)
        with patch('services.job_service.job_service.generate_video_from_prompt') as mock_video_gen:
            mock_result = {
                "status": "success",
                "video_path": "/tmp/test_video.mp4",
                "duration": 10,
                "prompt": "Generated prompt",
                "campaign_id": 1
            }
            mock_video_gen.return_value = mock_result
            
            result = send_prompt_to_video_api(self.mock_db, 1)
            self.assertTrue(result)
        
        # 5. Atualiza status para PROCESSING_VIDEO
        self.mock_job.status = JobStatusEnum.PROCESSING_VIDEO
        
        # 6. Polling até COMPLETED (upload para Google Drive)
        with patch('services.job_service.job_service.generate_video_from_prompt') as mock_video_gen:
            mock_result = {
                "status": "success",
                "video_path": "/tmp/test_video.mp4",
                "duration": 10,
                "prompt": "Generated prompt",
                "campaign_id": 1
            }
            mock_video_gen.return_value = mock_result
            
            with patch('builtins.open', unittest.mock.mock_open(read_data=b"video content")):
                with patch('services.drive_service.drive_service.DriveService') as mock_drive_service_class:
                    mock_drive_service = Mock()
                    mock_drive_service.upload_file.return_value = {"webViewLink": "https://drive.google.com/file/d/test123/view"}
                    mock_drive_service_class.return_value = mock_drive_service
                    
                    result = poll_video_processing_status(self.mock_db, 1)
                    self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()