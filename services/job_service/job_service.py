from sqlalchemy.orm import Session
from typing import Optional
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from models.entities import PipelineJob, Campaign, JobStatusEnum
from models.pydantic import PipelineJob as PipelineJobPydantic
from services.llm_service import get_llm_service

def initialize_new_job(db: Session, campaign_id: int, prompt: Optional[str] = None) -> PipelineJob:
    """
    Implementar função de inicialização de novo job com status PENDING
    
    Args:
        db: Sessão do banco de dados
        campaign_id: ID da campanha associada
        prompt: Prompt opcional para o job (geralmente None no início)
    
    Returns:
        PipelineJob criado com status PENDING
    """
    # Verifica se a campanha existe
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise ValueError(f"Campaign with id {campaign_id} not found")
    
    # Cria um novo PipelineJob com status PENDING
    job = PipelineJob(
        campaign_id=campaign_id,
        prompt=prompt,
        status=JobStatusEnum.PENDING
    )
    
    # Adiciona e faz commit no banco de dados
    db.add(job)
    db.commit()
    db.refresh(job)
    
    return job


def get_pending_jobs(db: Session):
    """
    Função auxiliar para obter jobs com status PENDING
    
    Args:
        db: Sessão do banco de dados
        
    Returns:
        Lista de jobs com status PENDING
    """
    return db.query(PipelineJob).filter(PipelineJob.status == JobStatusEnum.PENDING).all()


def fetch_and_process_next_pending_job(db: Session):
    """
    Implementar worker para buscar jobs PENDING no banco
    
    Args:
        db: Sessão do banco de dados
        
    Returns:
        Um único job PENDING para ser processado ou None se não houver
    """
    # Busca o primeiro job com status PENDING
    # Garantindo que apenas um job seja selecionado por vez
    pending_job = db.query(PipelineJob).filter(
        PipelineJob.status == JobStatusEnum.PENDING
    ).first()
    
    return pending_job


def update_job_status(db: Session, job_id: int, status: JobStatusEnum, 
                     prompt: Optional[str] = None, video_url: Optional[str] = None, 
                     error_message: Optional[str] = None):
    """
    Atualiza o status de um job e outros campos opcionais
    
    Args:
        db: Sessão do banco de dados
        job_id: ID do job a ser atualizado
        status: Novo status do job
        prompt: Novo prompt (opcional)
        video_url: URL do vídeo (opcional)
        error_message: Mensagem de erro (opcional)
        
    Returns:
        Job atualizado
    """
    job = db.query(PipelineJob).filter(PipelineJob.id == job_id).first()
    if not job:
        raise ValueError(f"Job with id {job_id} not found")
    
    job.status = status
    if prompt is not None:
        job.prompt = prompt
    if video_url is not None:
        job.video_url = video_url
    if error_message is not None:
        job.error_message = error_message
    
    db.commit()
    db.refresh(job)
    
    return job

async def process_pending_job_with_llm(db: Session, max_retries: int = 3):
    """
    Integrar `llm_service.py` com a geração de prompt para jobs PENDING

    Args:
        db: Sessão do banco de dados
        max_retries: Número máximo de tentativas para gerar o prompt

    Returns:
        True se o prompt foi gerado com sucesso, False caso contrário
    """
    # Pegar um job pendente
    job = fetch_and_process_next_pending_job(db)
    if not job:
        return False

    # Pegar a campanha associada para obter o briefing
    campaign = db.query(Campaign).filter(Campaign.id == job.campaign_id).first()
    if not campaign:
        error_msg = f"Campanha não encontrada para o job {job.id}"
        update_job_status(db, job.id, JobStatusEnum.FAILED, error_message=error_msg)
        return False

    # Tentar gerar o prompt usando o LLM
    llm_service = get_llm_service()
    last_error = None

    for attempt in range(max_retries):
        try:
            generated_prompt = await llm_service.generate_prompt_from_brief(campaign.briefing_text)
            if generated_prompt:
                # Atualizar o job com o prompt gerado e mudar o status
                update_job_status(db, job.id, JobStatusEnum.PROMPT_GENERATED, prompt=generated_prompt)
                return True
            else:
                last_error = f"Tentativa {attempt + 1}: Falha ao gerar o prompt"
        except Exception as e:
            last_error = f"Tentativa {attempt + 1}: Erro ao gerar prompt - {str(e)}"
            print(last_error)

    # Se chegou aqui, todas as tentativas falharam
    update_job_status(db, job.id, JobStatusEnum.FAILED, error_message=last_error or "Erro desconhecido")
    return False

def transition_job_status_pending_to_prompt_generated(db: Session, job_id: int, prompt: str) -> bool:
    """
    Implementar função de transição de status PENDING -> PROMPT_GENERATED

    Args:
        db: Sessão do banco de dados
        job_id: ID do job a ter o status alterado
        prompt: Prompt gerado a ser salvo no job

    Returns:
        True se a transição foi feita com sucesso, False caso contrário
    """
    try:
        # Obter o job pelo ID
        job = db.query(PipelineJob).filter(PipelineJob.id == job_id).first()
        if not job:
            print(f"Job com ID {job_id} não encontrado")
            return False

        # Verificar se o status atual é PENDING
        if job.status != JobStatusEnum.PENDING:
            print(f"Job com ID {job_id} não está no status PENDING, atual: {job.status.value}")
            return False

        # Atualizar o status para PROMPT_GENERATED e salvar o prompt
        update_job_status(db, job_id, JobStatusEnum.PROMPT_GENERATED, prompt=prompt)
        return True
    except Exception as e:
        print(f"Erro ao tentar transicionar o status do job {job_id}: {str(e)}")
        return False