from sqlalchemy.orm import Session
from typing import Optional
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from models.entities import PipelineJob, Campaign, JobStatusEnum
from models.pydantic import PipelineJob as PipelineJobPydantic


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