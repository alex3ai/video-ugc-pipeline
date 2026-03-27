import pytest
import os
from unittest.mock import patch, MagicMock

# Importar as funções necessárias para testar o fluxo completo
from api.routes import submit_campaign
from services.job_service import process_job
from services.llm_service import get_llm_service
from services.video_service import generate_video_from_prompt  # Atualizado para usar a função correta
from models.entities import Campaign, PipelineJob, JobStatusEnum
from database import SessionLocal

def test_end_to_end_complete_flow():
    """
    Testa o fluxo completo de ponta a ponta:
    1. Criação de campanha
    2. Processamento do job
    3. Geração de vídeo
    4. Upload para o Google Drive
    """
    # Criar uma campanha de teste
    campaign_data = {
        "name": "Test Campaign E2E",
        "briefing_text": "Create a promotional video about a new tech product focusing on its innovative features and benefits for users."
    }
    
    # Simular a criação da campanha
    with patch('services.job_service.initialize_new_job') as mock_initialize:
        mock_job = MagicMock()
        mock_job.id = 1
        mock_initialize.return_value = mock_job
        
        result = submit_campaign(campaign_data)
        
        assert result is not None
        assert "job_id" in result
    
    # Obter o ID do job criado
    job_id = result["job_id"]
    
    # Testar o processamento do job
    with patch('services.llm_service.get_llm_service') as mock_get_llm:
        # Mock do serviço de LLM
        mock_llm_service = MagicMock()
        mock_llm_service.generate_prompt_from_brief.return_value = "Test video script for tech product promotion"
        mock_get_llm.return_value = mock_llm_service
        
        # Mock do serviço de vídeo
        with patch('services.video_service.generate_video_from_prompt') as mock_generate_video:
            mock_generate_video.return_value = "/tmp/test_video.mp4"
            
            # Mock do serviço de upload para o Google Drive
            with patch('services.job_service.upload_video_to_drive') as mock_upload:
                mock_upload.return_value = "https://drive.google.com/file/d/test_video"
                
                # Processar o job
                success = process_job(job_id)
                
                # Verificar se o processamento foi bem-sucedido
                assert success is True
                
                # Verificar se as funções foram chamadas corretamente
                mock_llm_service.generate_prompt_from_brief.assert_called_once()
                mock_generate_video.assert_called_once()
                mock_upload.assert_called_once()
                
                # Verificar se o vídeo foi gerado com o conteúdo correto
                args, kwargs = mock_generate_video.call_args
                assert "Test video script" in args[0]

def test_e2e_with_mocked_services():
    """
    Testa o fluxo E2E com todos os serviços mockados
    """
    # Testar com serviços completamente mockados
    with patch('api.routes.CampaignEntity') as mock_campaign, \
         patch('api.routes.initialize_new_job') as mock_init_job, \
         patch('services.job_service.get_llm_service') as mock_get_llm, \
         patch('services.job_service.generate_video_from_prompt') as mock_gen_video, \
         patch('services.job_service.upload_video_to_drive') as mock_upload:
        
        # Configurar mocks
        mock_campaign_instance = MagicMock()
        mock_campaign_instance.id = 999
        mock_campaign_instance.name = "Mocked Test Campaign"
        mock_campaign.return_value = mock_campaign_instance
        
        mock_job = MagicMock()
        mock_job.id = 99
        mock_init_job.return_value = mock_job
        
        mock_llm_service = MagicMock()
        mock_llm_service.generate_prompt_from_brief.return_value = "Mocked video script"
        mock_get_llm.return_value = mock_llm_service
        
        mock_gen_video.return_value = "/tmp/mock_video.mp4"
        mock_upload.return_value = "https://drive.google.com/file/d/mock_video"
        
        # Dados da campanha
        campaign_data = {
            "name": "Mock Test Campaign",
            "briefing_text": "This is a mocked test campaign for E2E testing"
        }
        
        # Executar o fluxo
        result = submit_campaign(campaign_data)
        
        # Verificar resultados
        assert result is not None
        assert result["job_id"] == 99
        
        # Processar o job
        success = process_job(99)
        
        # Verificar se tudo foi chamado corretamente
        assert success is True
        mock_llm_service.generate_prompt_from_brief.assert_called_once()
        mock_gen_video.assert_called_once()
        mock_upload.assert_called_once()

if __name__ == "__main__":
    pytest.main([__file__])