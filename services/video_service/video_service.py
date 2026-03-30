import os
import tempfile
import time
from typing import Dict, Any, Optional
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from gradio_client import Client
from huggingface_hub import login, HfApi
from huggingface_hub.utils import RepositoryNotFoundError
from moviepy.editor import VideoFileClip, concatenate_videoclips
import requests
import logging

from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _authenticate_huggingface():
    """
    Verifica se o token do Hugging Face está disponível nas variáveis de ambiente
    """
    hf_token = os.getenv("HF_TOKEN") or os.getenv("HF_API_KEY")
    if not hf_token:
        logger.warning("Nenhum token Hugging Face encontrado nas variáveis de ambiente.")
        return None
    else:
        logger.info("Token Hugging Face encontrado nas variáveis de ambiente.")
        return hf_token


def validate_hf_space_access(space_id: str) -> bool:
    """
    Valida se o Space existe e está acessível
    """
    try:
        hf_token = _authenticate_huggingface()
        if not hf_token:
            logger.error("Token Hugging Face não configurado no ambiente")
            return False

        api = HfApi(token=hf_token)
        # Verifica se o Space existe com repo_type="space"
        api.repo_info(repo_id=space_id, repo_type="space")
        logger.info(f"Space {space_id} encontrado e acessível.")
        return True
    except RepositoryNotFoundError:
        logger.error(f"Space {space_id} não encontrado. Verifique o nome do repositório.")
        return False
    except Exception as e:
        logger.error(f"Não foi possível acessar o Space {space_id}: {e}")
        return False


def check_space_status(space_id: str):
    """
    Verifica o status atual do Space
    """
    try:
        hf_token = _authenticate_huggingface()
        if not hf_token:
            logger.error("Token Hugging Face não configurado no ambiente")
            return None

        api = HfApi(token=hf_token)
        runtime = api.get_space_runtime(space_id)
        
        # O retorno pode ser um dicionário ou objeto, vamos verificar
        if hasattr(runtime, 'stage'):
            status = runtime.stage.value if hasattr(runtime.stage, 'value') else runtime.stage
        else:
            # Se runtime for um dicionário, extrair o status
            status = runtime.get('stage', 'unknown') if isinstance(runtime, dict) else 'unknown'
            
        logger.info(f"Status do Space {space_id}: {status}")
        return status
    except Exception as e:
        logger.error(f"Não foi possível obter o status do Space {space_id}: {e}")
        return None


def test_video_api_connection():
    """
    Função de teste para conexão com API de vídeo
    """
    try:
        # Verificar autenticação
        hf_token = _authenticate_huggingface()
        if not hf_token:
            return False

        # Validar se o Space está acessível
        if not validate_hf_space_access(settings.HF_SPACE_MODEL):
            logger.error(f"O Space {settings.HF_SPACE_MODEL} não está acessível")
            return False

        # Verificar status do Space
        status = check_space_status(settings.HF_SPACE_MODEL)
        if not status:
            logger.warning(f"Não foi possível obter o status do Space {settings.HF_SPACE_MODEL}, continuando assim mesmo...")
        else:
            if status == "Sleeping":
                logger.info(f"O Space {settings.HF_SPACE_MODEL} está dormindo. Será ativado automaticamente.")
            elif status in ["Building", "Running"]:
                logger.info(f"O Space {settings.HF_SPACE_MODEL} está em estado {status}")

        # Testar a conexão com o modelo de vídeo - agora passando o token corretamente
        client = Client(settings.HF_SPACE_MODEL, token=hf_token)
        return True
    except Exception as e:
        logger.error(f"Erro ao testar conexão com API de vídeo: {e}")
        return False


def generate_video_with_huggingface(text_prompt: str) -> Optional[str]:
    """
    Gera um único vídeo com base no prompt de texto
    """
    try:
        logger.info(f"Gerando vídeo com prompt: {text_prompt[:50]}...")

        # Obter token
        hf_token = _authenticate_huggingface()
        if not hf_token:
            logger.error("Token Hugging Face não configurado no ambiente")
            return None

        # Validar o acesso ao Space antes de prosseguir
        if not validate_hf_space_access(settings.HF_SPACE_MODEL):
            logger.error(f"Space de vídeo {settings.HF_SPACE_MODEL} não está acessível")
            return None

        # Verificar status do Space
        status = check_space_status(settings.HF_SPACE_MODEL)
        if status and status == "Sleeping":
            logger.info("O Space está dormindo, aguardando wake-up...")
            # O cliente do Gradio já faz o wake-up automaticamente, então vamos continuar

        # Usar o Gradio Client para se conectar ao Space Hugging Face
        client = Client(settings.HF_SPACE_MODEL, token=hf_token)

        # Listar endpoints disponíveis para debug
        try:
            logger.info(f"Endpoints disponíveis no Space: {client.endpoints}")
        except:
            pass

        # Chamar o Space para gerar o vídeo
        # O nome do endpoint pode variar, vamos tentar diferentes possibilidades
        possible_endpoints = ["/infer", "/predict", "/generate", "/run"]
        result = None
        
        for endpoint in possible_endpoints:
            try:
                logger.info(f"Tentando endpoint: {endpoint}")
                result = client.predict(
                    text_prompt,
                    api_name=endpoint
                )
                if result:
                    break
            except Exception as e:
                logger.info(f"Endpoint {endpoint} falhou: {e}")
                continue

        if not result:
            logger.error("Nenhum endpoint funcionou para gerar o vídeo")
            return None

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


def warmup_space():
    """
    Acorda o Space se estiver dormindo antes de gerar vídeo
    """
    try:
        # Verificar autenticação
        hf_token = _authenticate_huggingface()
        if not hf_token:
            logger.error("Token Hugging Face não configurado no ambiente")
            return False

        # Validar o acesso ao Space antes de prosseguir
        if not validate_hf_space_access(settings.HF_SPACE_MODEL):
            logger.error(f"Space de vídeo {settings.HF_SPACE_MODEL} não está acessível")
            return False

        # Verificar status do Space
        status = check_space_status(settings.HF_SPACE_MODEL)
        if not status:
            logger.warning(f"Não foi possível obter o status do Space {settings.HF_SPACE_MODEL}")
            # Tentar mesmo assim
            client = Client(settings.HF_SPACE_MODEL, token=hf_token)
            logger.info("Space acordado e pronto.")
            return True

        if status == "Sleeping":
            logger.info(f"Space {settings.HF_SPACE_MODEL} está dormindo, acordando...")
            # O cliente do Gradio fará o wake-up automaticamente
            client = Client(settings.HF_SPACE_MODEL, token=hf_token)
            logger.info("Space acordado e pronto.")
        elif status in ["Running", "Building"]:
            logger.info(f"Space {settings.HF_SPACE_MODEL} já está ativo ({status}).")
            client = Client(settings.HF_SPACE_MODEL, token=hf_token)
        else:
            logger.info(f"Space {settings.HF_SPACE_MODEL} em estado {status}, tentando conectar...")
            client = Client(settings.HF_SPACE_MODEL, token=hf_token)

        return True
    except Exception as e:
        logger.warning(f"Warmup do Space falhou: {e}")
        return False


def generate_video_from_prompt(prompt: str) -> Optional[str]:
    """
    Gera um vídeo completo a partir de um prompt dividindo em segmentos
    """
    logger.info("Iniciando geração de vídeo a partir do prompt...")
    
    # Validar o acesso ao Space antes de começar o processo
    if not validate_hf_space_access(settings.HF_SPACE_MODEL):
        logger.error(f"Space de vídeo {settings.HF_SPACE_MODEL} não está acessível")
        return None

    # Warmup do Space para garantir que esteja ativo antes de gerar vídeo
    if not warmup_space():
        logger.error("Não foi possível inicializar o Space para geração de vídeo")
        return None

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

    # Concatenar os segmentos gerados
    final_video_path = concatenate_video_segments([segment1_path, segment2_path])
    
    # Remover arquivos temporários após a concatenação
    try:
        if segment1_path and os.path.exists(segment1_path):
            os.remove(segment1_path)
        if segment2_path and os.path.exists(segment2_path):
            os.remove(segment2_path)
    except Exception as e:
        logger.warning(f"Erro ao remover arquivos temporários: {e}")
    
    return final_video_path