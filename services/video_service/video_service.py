import os
import tempfile
import time
from typing import Dict, Any, Optional
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from gradio_client import Client
from moviepy.editor import VideoFileClip, concatenate_videoclips
import requests


def test_video_api_connection():
    """
    Função de teste para conexão com API de vídeo
    """
    try:
        # Testar se os pacotes necessários estão disponíveis
        import gradio_client
        import moviepy
        print("Dependências necessárias para geração de vídeo estão instaladas!")
        return True
    except ImportError as e:
        print(f"Erro: Dependências necessárias não encontradas: {str(e)}")
        return False


def generate_video_from_prompt(prompt: str, campaign_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """
    Gera um vídeo de 10 segundos a partir de um prompt de texto usando T2V grátis do Hugging Face
    
    Args:
        prompt (str): O prompt textual para geração do vídeo
        campaign_id (int, optional): ID da campanha associada
        
    Returns:
        dict: Informações sobre o vídeo gerado
    """
    try:
        # Criar diretório temporário para armazenar os vídeos
        temp_dir = settings.TEMP_VIDEO_DIR
        
        # Usar o modelo configurado no settings
        client = Client(settings.HF_SPACE_MODEL)
        
        # Gerar primeiro segmento de 5 segundos
        print("Gerando primeiro segmento de vídeo...")
        result_1 = client.predict(
            prompt,
            api_name="/predict"
        )
        
        # Salvar primeiro vídeo
        video_path_1 = os.path.join(temp_dir, "video_part_1.mp4")
        with open(video_path_1, 'wb') as f:
            with open(result_1, 'rb') as source:
                f.write(source.read())
        
        # Gerar segundo segmento de 5 segundos com o mesmo prompt
        print("Gerando segundo segmento de vídeo...")
        result_2 = client.predict(
            prompt,
            api_name="/predict"
        )
        
        # Salvar segundo vídeo
        video_path_2 = os.path.join(temp_dir, "video_part_2.mp4")
        with open(video_path_2, 'wb') as f:
            with open(result_2, 'rb') as source:
                f.write(source.read())
        
        # Combinar os vídeos com transição suave
        print("Combinando vídeos com transição...")
        combined_video_path = os.path.join(temp_dir, "video_final_10s.mp4")
        
        # Carregar os clips de vídeo
        clip1 = VideoFileClip(video_path_1)
        clip2 = VideoFileClip(video_path_2)
        
        # Cortar os clips para terem a duração configurada
        duration_per_segment = settings.VIDEO_DURATION_PER_SEGMENT
        clip1 = clip1.subclip(0, min(duration_per_segment, clip1.duration))
        clip2 = clip2.subclip(0, min(duration_per_segment, clip2.duration))
        
        # Obter duração da transição configurada
        fade_duration = settings.CROSSFADE_DURATION
        if clip1.duration > fade_duration and clip2.duration > fade_duration:
            # Aplicar crossfade
            clip1 = clip1.crossfadeout(fade_duration)
            clip2 = clip2.crossfadein(fade_duration)
            
            # Concatenar os vídeos
            final_clip = concatenate_videoclips([clip1, clip2], method="compose")
        else:
            # Se os vídeos forem muito curtos para a transição, apenas concatenar
            final_clip = concatenate_videoclips([clip1, clip2])
        
        # Exportar o vídeo combinado
        final_clip.write_videofile(combined_video_path, audio_codec='aac')
        
        # Fechar os clips para liberar recursos
        clip1.close()
        clip2.close()
        final_clip.close()
        
        # Retornar informações sobre o vídeo gerado
        return {
            "status": "success",
            "video_path": combined_video_path,
            "duration": duration_per_segment * 2,  # Aproximadamente 10 segundos
            "prompt": prompt,
            "campaign_id": campaign_id
        }
        
    except Exception as e:
        print(f"Erro ao gerar vídeo: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "prompt": prompt,
            "campaign_id": campaign_id
        }


def check_video_generation_status(job_id: str) -> Optional[Dict[str, Any]]:
    """
    Esta função não é aplicável com a nova abordagem pois a geração é síncrona
    """
    # Esta função não é mais necessária com a nova abordagem
    # A geração agora é feita de forma síncrona
    return {
        "status": "not_applicable",
        "message": "A geração de vídeo é feita de forma síncrona com a nova abordagem"
    }