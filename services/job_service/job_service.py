from sqlalchemy.orm import Session
import sys
import os
import asyncio
import time
from datetime import datetime
import logging
from typing import Optional
from database import SessionLocal
from models.entities import PipelineJob, JobStatusEnum, Campaign
from services.llm_service import get_llm_service
from services.video_service import generate_video_from_prompt
from services.drive_service import DriveService  # Atualizado para usar a classe correta

logger = logging.getLogger(__name__)

def initialize_new_job(db: Session, campaign_id: int) -> PipelineJob:
    """
    Inicializa um novo job para processamento de vídeo
    """
    try:
        # Criar novo job associado à campanha
        job = PipelineJob(
            campaign_id=campaign_id,
            status=JobStatusEnum.PENDING,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Salvar no banco de dados
        db.add(job)
        db.commit()
        db.refresh(job)
        
        logger.info(f"Novo job criado com ID: {job.id} para a campanha: {campaign_id}")
        return job
    except Exception as e:
        logger.error(f"Erro ao inicializar novo job para a campanha {campaign_id}: {e}")
        db.rollback()
        raise

def get_pending_jobs(db: Session) -> list:
    """
    Retorna todos os jobs com status PENDING
    """
    try:
        pending_jobs = db.query(PipelineJob).filter(
            PipelineJob.status == JobStatusEnum.PENDING
        ).all()
        
        logger.info(f"Encontrados {len(pending_jobs)} jobs pendentes")
        return pending_jobs
    except Exception as e:
        logger.error(f"Erro ao buscar jobs pendentes: {e}")
        return []

def update_job_status(db: Session, job_id: int, status: JobStatusEnum, error_message: str = None):
    """
    Atualiza o status de um job específico
    """
    try:
        job = db.query(PipelineJob).filter(PipelineJob.id == job_id).first()
        
        if not job:
            logger.error(f"Job com ID {job_id} não encontrado para atualização de status")
            return False
        
        job.status = status
        job.updated_at = datetime.utcnow()
        
        if error_message:
            job.error_message = error_message
        
        db.commit()
        logger.info(f"Status do job {job_id} atualizado para: {status}")
        return True
    except Exception as e:
        logger.error(f"Erro ao atualizar status do job {job_id}: {e}")
        db.rollback()
        return False

def process_job(job_id: int):
    """
    Processa um job de geração de vídeo usando as configurações corretas
    """
    session = SessionLocal()
    try:
        # Obter o job do banco de dados
        job = session.query(PipelineJob).filter(PipelineJob.id == job_id).first()
        
        if not job:
            logger.error(f"Job com ID {job_id} não encontrado")
            return False
            
        logger.info(f"Iniciando processamento do job {job_id} com status: {job.status}")
        
        # Atualizar status para PROCESSING
        job.status = JobStatusEnum.PROCESSING
        job.updated_at = datetime.utcnow()
        session.commit()
        
        # Obter o serviço de LLM e gerar o prompt do briefing
        llm_service = get_llm_service()
        
        # Corrigir chamada assíncrona
        video_script = asyncio.run(llm_service.generate_prompt_from_brief(job.campaign.briefing_text))
        
        if not video_script:
            error_msg = "Falha ao gerar roteiro com LLM"
            logger.error(f"{error_msg} para o job {job_id}")
            update_job_status(session, job_id, JobStatusEnum.FAILED, error_msg)
            return False
            
        logger.info(f"Roteiro gerado para o job {job_id}: {video_script[:100]}...")
        
        # Atualizar o prompt no job
        job.prompt = video_script
        job.updated_at = datetime.utcnow()
        session.commit()
        
        # Gerar o vídeo a partir do roteiro
        logger.info(f"Gerando vídeo para o job {job_id}...")
        video_path = generate_video_from_prompt(video_script)
        
        if not video_path or not video_path.endswith('.mp4'):
            error_msg = "Falha ao gerar vídeo"
            logger.error(f"{error_msg} para o job {job_id}")
            update_job_status(session, job_id, JobStatusEnum.FAILED, error_msg)
            return False
            
        logger.info(f"Vídeo gerado com sucesso para o job {job_id}: {video_path}")
        
        # Upload do vídeo para o Google Drive
        logger.info(f"Fazendo upload do vídeo para o Google Drive...")
        video_url = upload_video_to_drive(video_path, f"video_job_{job_id}.mp4")
        
        if not video_url:
            error_msg = "Falha ao fazer upload do vídeo para o Google Drive"
            logger.error(f"{error_msg} para o job {job_id}")
            update_job_status(session, job_id, JobStatusEnum.FAILED, error_msg)
            return False
            
        logger.info(f"Vídeo enviado para o Google Drive: {video_url}")
        
        # Atualizar status para COMPLETED
        update_job_status(session, job_id, JobStatusEnum.COMPLETED)
        job.video_url = video_url
        job.updated_at = datetime.utcnow()
        session.commit()
        
        logger.info(f"Job {job_id} concluído com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao processar job {job_id}: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()


def load_config():
    """Carrega as configurações do ambiente"""
    config = {
        'DRIVE_FOLDER_ID': os.getenv('DRIVE_FOLDER_ID'),
        'DRIVE_SHARE_WITH': os.getenv('DRIVE_SHARE_WITH')
    }
    
    # Verifica configurações obrigatórias
    if not config['DRIVE_FOLDER_ID']:
        logger.warning("DRIVE_FOLDER_ID não configurado. Usando pasta padrão do Drive.")
    
    if not config['DRIVE_SHARE_WITH']:
        logger.debug("DRIVE_SHARE_WITH não configurado. Não compartilhará o arquivo.")
    
    return config

def upload_video_to_drive(video_path: str, filename: str) -> Optional[str]:
    """
    Faz upload do vídeo para o Google Drive usando as configurações corretas
    """
    try:
        # Carregar configurações
        config = load_config()
        
        # Ler o conteúdo do arquivo de vídeo
        with open(video_path, 'rb') as video_file:
            video_bytes = video_file.read()
        
        # Inicializar o serviço de Drive com configurações
        drive_service = DriveService()
        
        # Configurar parâmetros do upload
        upload_kwargs = {
            'name': filename,
            'content': video_bytes,
            'folder_id': config['DRIVE_FOLDER_ID']
        }
        
        # Adicionar parâmetros opcionais se existirem
        if config['DRIVE_SHARE_WITH']:
            upload_kwargs['share_with'] = config['DRIVE_SHARE_WITH']
        
        # Fazer upload do arquivo
        result = drive_service.upload_file(**upload_kwargs)
        
        if not result:
            logger.error("Falha no upload do vídeo para o Google Drive")
            return None
            
        # Retornar o link do arquivo
        file_id = result.get('id')
        if not file_id:
            logger.error("Resposta do Drive não contém ID do arquivo")
            return None
            
        return f"https://drive.google.com/file/d/{file_id}/view"
        
    except Exception as e:
        logger.error(f"Erro ao fazer upload do vídeo para o Google Drive: {e}")
        return None