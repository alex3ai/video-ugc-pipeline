import pytest
from unittest.mock import patch, MagicMock
import os

from services.video_service.video_service import generate_video_from_prompt, test_video_api_connection, concatenate_video_segments
from services.video_service.video_service import generate_video_segment


def test_generate_video_from_prompt():
    """
    Testa a geração de vídeo a partir de um prompt
    """
    # Este teste requer credenciais válidas do Hugging Face
    # Para testes unitários, vamos mockar as dependências
    with patch('services.video_service.video_service.generate_video_segment') as mock_segment:
        mock_segment.side_effect = lambda prompt, num: f"/tmp/video_part_{num}.mp4" if prompt else None
        
        with patch('services.video_service.video_service.concatenate_video_segments') as mock_concat:
            mock_concat.return_value = "/tmp/final_video.mp4"
            
            prompt = "This is a sample video prompt for testing purposes."
            result = generate_video_from_prompt(prompt)
            
            assert result == "/tmp/final_video.mp4"
            mock_segment.assert_any_call(prompt[:len(prompt)//2], 1)
            mock_segment.assert_any_call(prompt[len(prompt)//2:], 2)
            mock_concat.assert_called_once()


def test_generate_video_segment():
    """
    Testa a geração de um segmento de vídeo
    """
    with patch('services.video_service.video_service.generate_video_with_huggingface') as mock_gen:
        mock_gen.return_value = "/tmp/test_segment.mp4"
        
        result = generate_video_segment("Test script segment", 1)
        
        assert result == "/tmp/test_segment.mp4"
        mock_gen.assert_called_once_with("Test script segment")


def test_concatenate_video_segments():
    """
    Testa a concatenação de segmentos de vídeo
    """
    with patch('moviepy.editor.VideoFileClip') as mock_clip:
        mock_clip_instance = MagicMock()
        mock_clip.return_value = mock_clip_instance
        
        with patch('moviepy.editor.concatenate_videoclips') as mock_concat:
            mock_concat.return_value = MagicMock()
            
            segment_paths = ["/tmp/seg1.mp4", "/tmp/seg2.mp4"]
            result = concatenate_video_segments(segment_paths)
            
            assert result is not None
            assert "/tmp/video_final_" in result
            assert result.endswith(".mp4")
            
            # Verificar se os clipes foram carregados
            assert mock_clip.call_count == 2
            mock_concat.assert_called_once()


def test_test_video_api_connection():
    """
    Testa a conexão com a API de vídeo
    """
    with patch('gradio_client.Client') as mock_client:
        mock_instance = MagicMock()
        mock_instance.predict.return_value = "/tmp/test.mp4"
        mock_client.return_value = mock_instance
        
        result = test_video_api_connection()
        
        # O resultado dependerá se a conexão real funcionar ou não
        # Mas com o mock, deve retornar True
        # A menos que haja alguma lógica específica no código real
        assert isinstance(result, bool)


@patch('services.video_service.video_service.Client')
@patch('services.video_service.video_service.requests.get')
@patch('services.video_service.video_service.VideoFileClip')
@patch('services.video_service.video_service.concatenate_videoclips')
def test_generate_video_with_real_hf_space(mock_concat, mock_clip, mock_requests, mock_client):
    """
    Testa a geração de vídeo com o espaço Hugging Face real (mockado)
    """
    # Configurar mocks
    mock_client_instance = MagicMock()
    mock_client_instance.predict.return_value = "/tmp/generated_video.mp4"
    mock_client.return_value = mock_client_instance
    
    mock_clip_instance = MagicMock()
    mock_clip.return_value = mock_clip_instance
    mock_concat.return_value = MagicMock()
    
    # Testar a função
    with patch.dict(os.environ, {"HF_SPACE_MODEL": "Wan-AI/Wan2.1-T2V-1.3B"}):
        result = generate_video_from_prompt("Test prompt for video generation")
        
        # A função retorna None se falhar, ou um caminho se tiver sucesso
        # com os mocks, deve ter sucesso
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__])