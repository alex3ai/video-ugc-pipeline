import os
import tempfile
import time
from typing import Dict, Any, Optional
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from gradio_client import Client
from moviepy.editor import VideoFileClip, concatenate_videoclips
import requests
import logging

from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_video_api_connection():
    """
    Função de teste para conexão com API de vídeo
    """
    try:
        # Testar a conexão com o modelo de vídeo
        client = Client(settings.HF_SPACE_MODEL)
        return True
    except Exception as e:
        logger.error(f"Erro ao testar conexão com API de vídeo: {e}")
        return False


def generate_video_with_huggingface(text_prompt: str) -> Optional[str]:
    """
    Gera um único vídeo de até 5 segundos com base no prompt de texto
    """
    try:
        logger.info(f"Gerando vídeo com prompt: {text_prompt[:50]}...")
        
        # Usar o Gradio Client para se conectar ao espaço Hugging Face
        client = Client(settings.HF_SPACE_MODEL)
        
        # Chamar o espaço para gerar o vídeo
        result = client.predict(
            text_prompt,
            api_name="/infer"
        )
        
        # Retorna o caminho para o vídeo gerado
        return result
    except Exception as e:
        logger.error(f"Erro ao gerar vídeo com Hugging Face: {e}")
        return None


def generate_video_segment(prompt: str, segment_number: int) -> Optional[str]:
    """
    Gera um segmento de vídeo usando o modelo Wan2.1-T2V-1.3B
    """
    logger.info(f"Iniciando geração do segmento {segment_number}: {prompt[:60]}...")
    
    # Gerar o vídeo com o modelo de texto fornecido
    video_path = generate_video_with_huggingface(prompt)
    
    if video_path:
        logger.info(f"Segmento {segment_number} gerado com sucesso: {video_path}")
        return video_path
    else:
        logger.error(f"Falha ao gerar segmento {segment_number}")
        return None


def concatenate_video_segments(segment_paths: list) -> Optional[str]:
    """
    Concatena múltiplos segmentos de vídeo com transições suaves
    """
    try:
        logger.info(f"Concatenando {len(segment_paths)} segmentos de vídeo...")
        
        # Carregar todos os clipes de vídeo
        clips = []
        for path in segment_paths:
            if path and os.path.exists(path):
                clip = VideoFileClip(path)
                clips.append(clip)
                logger.info(f"Carregado clipe: {path}")
            else:
                logger.warning(f"Caminho de vídeo inválido ou não encontrado: {path}")
        
        if not clips:
            logger.error("Nenhum clipe de vídeo válido encontrado para concatenação")
            return None
        
        # Aplicar crossfade entre os clipes para transição suave
        if len(clips) > 1:
            logger.info("Aplicando concatenação com crossfade entre os clipes...")
            # Aplica crossfade entre os clipes consecutivos
            final_clip = concatenate_videoclips(clips, 
                                               method='compose', 
                                               padding=settings.CROSSFADE_DURATION)
        else:
            final_clip = clips[0]
        
        # Salvar o vídeo final temporariamente
        temp_dir = settings.TEMP_VIDEO_DIR
        output_filename = os.path.join(temp_dir, f"video_final_{int(time.time())}.mp4")
        
        logger.info(f"Salvando vídeo concatenado: {output_filename}")
        final_clip.write_videofile(output_filename, codec='libx264', audio_codec='aac')
        
        # Fechar os clipes para liberar recursos
        for clip in clips:
            clip.close()
        final_clip.close()
        
        logger.info(f"Vídeo final salvo em: {output_filename}")
        return output_filename
        
    except Exception as e:
        logger.error(f"Erro ao concatenar vídeos: {e}")
        import traceback
        traceback.print_exc()
        return None


def generate_video_from_prompt(prompt: str) -> Optional[str]:
    """
    Gera um vídeo completo a partir de um prompt dividindo em segmentos
    """
    logger.info("Iniciando geração de vídeo a partir do prompt...")
    
    # Dividir o prompt em duas partes para gerar dois vídeos de 5 segundos cada
    # e concatenar para obter um vídeo de 10 segundos com transição suave
    prompt_length = len(prompt)
    mid_point = prompt_length // 2
    
    # Dividir o prompt em duas partes aproximadamente iguais
    part1 = prompt[:mid_point]
    part2 = prompt[mid_point:]
    
    # Garantir que ambas as partes tenham algum conteúdo significativo
    if len(part1.strip()) < 10:
        part1 = prompt[:min(len(prompt)//2 + 20, len(prompt))]
        part2 = prompt[min(len(prompt)//2 + 20, len(prompt)):]
    
    logger.info(f"Divisão do prompt: Parte 1 ({len(part1)} chars), Parte 2 ({len(part2)} chars)")
    
    # Gerar os dois segmentos de vídeo
    segment1_path = generate_video_segment(part1, 1)
    if not segment1_path:
        logger.error("Falha ao gerar o primeiro segmento de vídeo")
        return None
    
    segment2_path = generate_video_segment(part2, 2)
    if not segment2_path:
        logger.error("Falha ao gerar o segundo segmento de vídeo")
        return None
    
    # Concatenar os segmentos
    final_video_path = concatenate_video_segments([segment1_path, segment2_path])
    
    # Remover os arquivos temporários dos segmentos individuais
    try:
        if segment1_path and os.path.exists(segment1_path):
            os.remove(segment1_path)
            logger.info(f"Arquivo temporário removido: {segment1_path}")
        if segment2_path and os.path.exists(segment2_path):
            os.remove(segment2_path)
            logger.info(f"Arquivo temporário removido: {segment2_path}")
    except Exception as e:
        logger.warning(f"Erro ao remover arquivos temporários: {e}")
    
    return final_video_path