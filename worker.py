import time
import threading
from typing import Optional
from database import SessionLocal
from models.entities import PipelineJob, JobStatusEnum
from services.job_service import get_pending_jobs, update_job_status, process_job
from config import settings

def run_pipeline_worker():
    """
    Função principal do worker que verifica periodicamente por jobs pendentes
    e os processa conforme necessário.
    """
    print("Iniciando worker da pipeline de vídeo UGC...")
    
    while True:
        try:
            print("Verificando jobs pendentes...")
            
            # Obter sessão do banco de dados
            db = SessionLocal()
            
            try:
                # Pegar jobs pendentes
                pending_jobs = get_pending_jobs(db)
                print(f"Encontrados {len(pending_jobs)} jobs pendentes")
                
                # Processar cada job pendente
                for job in pending_jobs:
                    print(f"Processando job ID: {job.id} com status: {job.status}")
                    
                    # Atualizar status do job para PROCESSING
                    update_job_status(db, job.id, JobStatusEnum.PROCESSING)
                    
                    # Processar o job em uma thread separada para permitir concorrência
                    job_thread = threading.Thread(
                        target=lambda j_id: process_job(j_id),
                        args=(job.id,)
                    )
                    job_thread.start()
                    
            finally:
                # Fechar a sessão do banco de dados
                db.close()
            
            print(f"Aguardando {settings.REQUEST_TIMEOUT} segundos antes da próxima verificação...")
            
            # Aguardar antes de verificar novamente
            time.sleep(settings.REQUEST_TIMEOUT)
            
        except KeyboardInterrupt:
            print("Worker foi interrompido pelo usuário")
            break
        except Exception as e:
            print(f"Erro no worker: {e}")
            import traceback
            traceback.print_exc()
            
            # Aguardar antes de tentar novamente para evitar loops infinitos
            time.sleep(settings.REQUEST_TIMEOUT)

if __name__ == "__main__":
    run_pipeline_worker()