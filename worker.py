"""
Worker script para processar jobs na pipeline de vídeo UGC
Este script executa continuamente o ciclo de estado dos jobs:
PENDING -> PROMPT_GENERATED -> PROCESSING_VIDEO -> COMPLETED
"""
import asyncio
import time
import sys
import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Adicionando o diretório raiz ao path para permitir imports relativos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.entities import PipelineJob, JobStatusEnum
from services.job_service.job_service import (
    get_pending_jobs,
    process_pending_job_with_llm,
    send_prompt_to_video_api,
    poll_video_processing_status,
    upload_video_to_drive
)
from config import settings
from database import engine, SessionLocal


def run_pipeline_worker():
    """
    Executar o worker principal que processa jobs na fila
    """
    print("Iniciando worker da pipeline de vídeo UGC...")
    
    try:
        while True:
            # Criar nova sessão de banco de dados em cada iteração
            db = SessionLocal()
            
            try:
                # Obter jobs pendentes
                pending_jobs = get_pending_jobs(db)
                print(f"\nVerificando {len(pending_jobs)} jobs pendentes...")
                
                # Processar cada job pendente
                for job in pending_jobs:
                    print(f"\nProcessando job ID: {job.id} com status: {job.status.value}")
                    
                    # Atualizar o job para PROCESSING
                    if job.status == JobStatusEnum.PENDING:
                        print(f"Processando job {job.id} com LLM...")
                        try:
                            llm_success = asyncio.run(process_pending_job_with_llm(db))
                            
                            if llm_success:
                                db.refresh(job)
                                print(f"Job {job.id} atualizado para: {job.status.value}")
                                
                                if job.status == JobStatusEnum.PROMPT_GENERATED:
                                    print(f"Enviando job {job.id} para API de vídeo...")
                                    video_api_success = send_prompt_to_video_api(db, job.id)
                                    
                                    if video_api_success:
                                        print(f"Job {job.id} enviado para processamento de vídeo")
                                    else:
                                        print(f"Falha ao enviar job {job.id} para API de vídeo")
                            else:
                                print(f"Falha no processamento do job {job.id} com LLM")
                        except Exception as e:
                            print(f"Erro ao processar job {job.id} com LLM: {str(e)}")
                            import traceback
                            traceback.print_exc()
                
                # Processar jobs que estão aguardando processamento de vídeo
                processing_video_jobs = db.query(PipelineJob).filter(
                    PipelineJob.status == JobStatusEnum.PROCESSING_VIDEO
                ).all()
                
                for job in processing_video_jobs:
                    print(f"Verificando status do vídeo para job ID: {job.id}")
                    try:
                        poll_result = poll_video_processing_status(db, job.id)
                        
                        if poll_result:
                            print(f"Polling concluído para job {job.id}")
                        else:
                            print(f"Polling ainda em andamento para job {job.id}")
                    except Exception as e:
                        print(f"Erro ao fazer polling para job {job.id}: {str(e)}")
                        import traceback
                        traceback.print_exc()
                
                # Processar jobs que estão com status UPLOAD_FAILED para tentar novamente
                try:
                    upload_failed_jobs = db.query(PipelineJob).filter(
                        PipelineJob.status == JobStatusEnum.UPLOAD_FAILED
                    ).all()
                    
                    for job in upload_failed_jobs:
                        print(f"Tentando fazer upload para Google Drive novamente para job ID: {job.id}")
                        
                        # Tenta fazer upload novamente com o video_url do job
                        if job.video_url:  # Este campo normalmente estaria vazio para UPLOAD_FAILED
                            # Nesse caso, teríamos que tentar obter o vídeo da API de vídeo novamente
                            # ou verificar se há alguma forma de recuperar o vídeo
                            print(f"Recuperando vídeo para job {job.id}")
                        else:
                            # Marcar como falha permanente?
                            print(f"Não há vídeo para fazer upload do job {job.id}")
                except AttributeError:
                    # UPLOAD_FAILED status might not be defined yet
                    print("UPLOAD_FAILED status not available in JobStatusEnum, skipping this check")
                
            except Exception as e:
                print(f"Erro ao processar jobs: {str(e)}")
                import traceback
                traceback.print_exc()
            finally:
                db.close()
            
            # Aguardar antes da próxima verificação
            print("\nAguardando 30 segundos antes da próxima verificação...")
            time.sleep(30)
    
    except KeyboardInterrupt:
        print("\nWorker interrompido pelo usuário.")
    except Exception as e:
        print(f"\nErro crítico no worker: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Check if required environment variables are set
    if not settings.VIDEO_API_KEY:
        print("AVISO: VIDEO_API_KEY não está definida. O processamento de vídeo não funcionará.")
    
    if not settings.GOOGLE_CREDENTIALS_PATH:
        print("AVISO: GOOGLE_CREDENTIALS_PATH não está definida. O upload para Google Drive não funcionará.")
    
    if not (settings.GROK_API_KEY or settings.LLAMA_API_KEY or settings.HF_API_KEY):
        print("AVISO: Nenhuma chave de API para LLM está definida. A geração de prompts não funcionará.")
    
    run_pipeline_worker()