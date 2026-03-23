import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Chaves e configurações para o Gemini
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Configurações para a API de vídeo
    VIDEO_API_URL: str = os.getenv("VIDEO_API_URL", "https://api.example.com")
    VIDEO_API_KEY: str = os.getenv("VIDEO_API_KEY", "")
    
    # Configurações para o Google Drive
    GOOGLE_CREDENTIALS_PATH: str = os.getenv("GOOGLE_CREDENTIALS_PATH", "")
    GOOGLE_DRIVE_FOLDER_ID: str = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "")
    
    # Configurações do banco de dados
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./video_ugc_pipeline.db")
    
    # Configurações de timeout
    VIDEO_RENDER_TIMEOUT: int = int(os.getenv("VIDEO_RENDER_TIMEOUT", "600"))  # 10 minutos em segundos
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))  # 30 segundos padrão
    
    # Configurações de tentativas
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    
    class Config:
        case_sensitive = True


settings = Settings()

# Função para validar se todas as chaves essenciais estão presentes
def validate_settings():
    errors = []
    
    if not settings.GEMINI_API_KEY:
        errors.append("GEMINI_API_KEY não está definida")
    
    if not settings.VIDEO_API_KEY:
        errors.append("VIDEO_API_KEY não está definida")
    
    if not settings.GOOGLE_CREDENTIALS_PATH:
        errors.append("GOOGLE_CREDENTIALS_PATH não está definida")
    
    if errors:
        raise ValueError(f"Erros de configuração encontrados: {'; '.join(errors)}")
    
    print("Todas as configurações essenciais estão presentes")


if __name__ == "__main__":
    # Testar a validação ao iniciar
    try:
        validate_settings()
    except ValueError as e:
        print(f"Aviso: {e}")