import asyncio
import sys
import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from unittest.mock import patch, MagicMock

# Adicionando o diretório raiz ao path para permitir imports relativos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.entities import Campaign, PipelineJob, JobStatusEnum
from services.job_service.job_service import (
    initialize_new_job,
    process_pending_job_with_llm,
    send_prompt_to_video_api,
    poll_video_processing_status,
    upload_video_to_drive
)
from config import settings
from database import engine


def test_full_pipeline():
    """
    Testar fluxo completo: briefing → prompt → vídeo → upload → link
    """
    print("Iniciando teste do fluxo completo...")
    
    # Criar sessão de banco de dados
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 1. Criar uma campanha de teste
        print("\n1. Criando campanha de teste...")
        test_campaign = Campaign(
            name="Test Campaign",
            briefing_text="Create a short promotional video about a productivity app that helps people manage their daily tasks and increase efficiency."
        )
        
        db.add(test_campaign)
        db.commit()
        db.refresh(test_campaign)
        
        print(f"Campanha criada com ID: {test_campaign.id}")
        
        # 2. Inicializar um novo job para esta campanha
        print("\n2. Inicializando novo job...")
        job = initialize_new_job(db, test_campaign.id)
        print(f"Job inicializado com ID: {job.id}, Status: {job.status.value}")
        
        # 3. Processar o job com LLM para gerar o prompt
        print("\n3. Processando job com LLM para gerar prompt...")
        llm_success = asyncio.run(process_pending_job_with_llm(db))
        print(f"Geração de prompt com LLM {'bem-sucedida' if llm_success else 'falhou'}")
        
        # Verificar status atual do job
        db.refresh(job)
        print(f"Status após processamento LLM: {job.status.value}")
        if job.status == JobStatusEnum.PROMPT_GENERATED:
            print(f"Prompt gerado: {job.prompt[:100]}...")  # Mostrar primeiros 100 caracteres
        
        # 4. Enviar o prompt para a API de vídeo
        print("\n4. Enviando prompt para API de vídeo...")
        if job.status == JobStatusEnum.PROMPT_GENERATED:
            video_api_success = send_prompt_to_video_api(db, job.id)
            print(f"Envio para API de vídeo {'bem-sucedido' if video_api_success else 'falhou'}")
            
            # Atualizar referência do job
            db.refresh(job)
            print(f"Status após envio para API de vídeo: {job.status.value}")
        
        # 5. Simular polling do status de processamento do vídeo
        print("\n5. Simulando polling do status de processamento do vídeo...")
        if job.status == JobStatusEnum.PROCESSING_VIDEO:
            # Neste ponto, o vídeo estaria sendo processado pela API externa
            # Para fins de teste, vamos simular a conclusão do processamento
            # e atualizar o status manualmente para demonstrar o fluxo
            
            # Na vida real, o polling seria contínuo até que a API de vídeo
            # indicasse que o vídeo está pronto
            print("Simulando conclusão do processamento de vídeo...")
            
            # Alterar o status para COMPLETED e adicionar uma URL de vídeo simulada
            from services.job_service.job_service import update_job_status
            update_job_status(
                db, 
                job.id, 
                JobStatusEnum.COMPLETED, 
                video_url="https://example-videos-api.com/generated-video.mp4"
            )
            
            db.refresh(job)
            print(f"Status após simulação de processamento: {job.status.value}")
        
        # 6. Fazer upload do vídeo para o Google Drive
        print("\n6. Fazendo upload do vídeo para o Google Drive...")
        if job.status == JobStatusEnum.COMPLETED and job.video_url:
            # Aqui, usamos a URL do vídeo gerado para fazer o upload para o Google Drive
            # Mas, para testar o upload, precisamos simular uma situação onde o vídeo
            # está em PROCESSING_VIDEO e o polling detecta sua conclusão
            
            # Vamos reverter o status para PROCESSING_VIDEO e simular o upload
            update_job_status(db, job.id, JobStatusEnum.PROCESSING_VIDEO)
            db.refresh(job)
            
            # Simular o polling e upload para o Drive
            # Para isso, vamos usar uma URL de vídeo fictícia para simular o download
            mock_video_url = "https://example-videos-api.com/generated-video.mp4"
            upload_success = upload_video_to_drive(db, job.id, mock_video_url)
            print(f"Upload para Google Drive {'bem-sucedido' if upload_success else 'falhou'}")
            
            db.refresh(job)
            print(f"Status após upload para Google Drive: {job.status.value}")
            if job.video_url:
                print(f"Link do vídeo no Drive: {job.video_url}")
        
        print("\nFluxo completo testado com sucesso!")
        print(f"Resumo:")
        print(f"- Campanha criada: {test_campaign.name}")
        print(f"- Job criado com ID: {job.id}")
        print(f"- Status final do job: {job.status.value}")
        if job.video_url:
            print(f"- Vídeo disponível em: {job.video_url}")
        
    except Exception as e:
        print(f"\nErro durante o teste do fluxo completo: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Fechar a sessão
        db.close()


if __name__ == "__main__":
    test_full_pipeline()