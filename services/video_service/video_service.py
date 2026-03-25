import os
import requests
import time
from typing import Dict, Any, Optional
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from config import settings


def test_video_api_connection():
    """
    Função de teste para conexão com API de vídeo
    """
    # Esta função verifica se é possível conectar-se à API de vídeo
    api_url = settings.VIDEO_API_URL
    api_key = settings.VIDEO_API_KEY
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Teste simples para verificar a conexão
    try:
        response = requests.get(f"{api_url}/test", headers=headers, timeout=settings.REQUEST_TIMEOUT)
        
        if response.status_code == 200:
            print("Conexão com a API de vídeo bem-sucedida!")
            return True
        else:
            print(f"Falha na conexão com a API de vídeo. Status: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar com a API de vídeo: {str(e)}")
        return False


def generate_video_from_prompt(prompt: str, campaign_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """
    Gera um vídeo a partir de um prompt de texto
    
    Args:
        prompt (str): O prompt textual para geração do vídeo
        campaign_id (int, optional): ID da campanha associada
        
    Returns:
        dict: Informações sobre a requisição de geração do vídeo
    """
    api_url = settings.VIDEO_API_URL
    api_key = settings.VIDEO_API_KEY
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "prompt": prompt,
        "campaign_id": campaign_id,
        "duration": 5,  # Duração padrão de 5 segundos
        "resolution": "720p"
    }
    
    try:
        response = requests.post(f"{api_url}/generate", json=payload, headers=headers, timeout=settings.REQUEST_TIMEOUT)
        
        if response.status_code in [200, 201, 202]:
            return response.json()
        elif response.status_code == 503:
            # Manipular resposta 503 (Cold Start)
            print("Recebido status 503 - Serviço temporariamente indisponível (Cold Start)")
            return {"status": "cold_start", "retry_after": 30}  # Tentar novamente após 30 segundos
        elif response.status_code == 410:
            # API descontinuada
            print(f"API descontinuada. Status: {response.status_code}, Response: {response.text}")
            return {"status": "discontinued", "error": response.text}
        else:
            print(f"Erro ao gerar vídeo: {response.status_code}, Response: {response.text}")
            return {"status": "error", "error": response.text}
            
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição de geração de vídeo: {str(e)}")
        return {"status": "error", "error": str(e)}


def check_video_generation_status(job_id: str) -> Optional[Dict[str, Any]]:
    """
    Verifica o status de uma requisição de geração de vídeo
    
    Args:
        job_id (str): ID da requisição de geração de vídeo
        
    Returns:
        dict: Status da requisição de geração de vídeo
    """
    api_url = settings.VIDEO_API_URL
    api_key = settings.VIDEO_API_KEY

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(f"{api_url}/status/{job_id}", headers=headers, timeout=settings.REQUEST_TIMEOUT)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erro ao verificar status do vídeo: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição de verificação de status: {str(e)}")
        return None