import os
import requests
from typing import Dict, Any, Optional


def test_video_api_connection():
    """
    Função de teste para conexão com API de vídeo
    """
    # Esta função verifica se é possível conectar-se à API de vídeo
    api_url = os.getenv("VIDEO_API_URL", "https://api.example.com")
    api_key = os.getenv("VIDEO_API_KEY", "")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Teste simples para verificar a conexão
    try:
        response = requests.get(f"{api_url}/test", headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("Conexão com a API de vídeo bem-sucedida!")
            return True
        else:
            print(f"Falha na conexão com a API de vídeo. Status: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar com a API de vídeo: {str(e)}")
        return False