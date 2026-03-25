from sqlalchemy.orm import Session
from typing import Optional
import sys
import os
import requests
import time
from datetime import datetime, timedelta
import tempfile
import uuid
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from models.entities import PipelineJob, Campaign, JobStatusEnum
from models.pydantic import PipelineJob as PipelineJobPydantic
from services.llm_service import get_llm_service
from services.drive_service.drive_service import DriveService
from services.video_service.video_service import generate_video_from_prompt
from config import settings


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
    # Utiliza um lock pessimista para evitar que outros workers selecionem o mesmo job
    pending_job = db.query(PipelineJob).filter(
        PipelineJob.status == JobStatusEnum.PENDING
    ).with_for_update().first()
    
    if pending_job:
        # Atualiza o status para PROCESSING para indicar que este job está sendo processado
        pending_job.status = JobStatusEnum.PROCESSING
        db.commit()
        db.refresh(pending_job)
    
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

def send_prompt_to_video_api(db: Session, job_id: int) -> bool:
    """
    Implementar função de envio do prompt para serviço de geração de vídeo (nova abordagem)

    Args:
        db: Sessão do banco de dados
        job_id: ID do job que contém o prompt a ser enviado

    Returns:
        True se o prompt foi enviado com sucesso e o job está PROCESSING_VIDEO, False caso contrário
    """
    # Obter o job pelo ID
    job = db.query(PipelineJob).filter(PipelineJob.id == job_id).first()
    if not job:
        print(f"Job com ID {job_id} não encontrado")
        return False

    # Verificar se o status atual é PROMPT_GENERATED (necessário para enviar para o serviço de vídeo)
    if job.status != JobStatusEnum.PROMPT_GENERATED:
        print(f"Job com ID {job_id} não está no status PROMPT_GENERATED, atual: {job.status.value}")
        return False

    try:
        # Gerar vídeo usando o novo serviço baseado em Hugging Face Spaces
        result = generate_video_from_prompt(job.prompt, campaign_id=job.campaign_id)

        if result and result.get("status") == "success":
            # O vídeo foi gerado com sucesso, atualizar o status do job para PROCESSING_VIDEO
            update_job_status(db, job_id, JobStatusEnum.PROCESSING_VIDEO)
            print(f"Vídeo gerado com sucesso. Job ID: {job_id}, Status: PROCESSING_VIDEO")
            return True
        else:
            # Ocorreu um erro na geração do vídeo
            error_message = result.get("error", "Erro desconhecido na geração do vídeo") if result else "Falha desconhecida na geração do vídeo"
            print(f"Falha ao gerar o vídeo: {error_message}")
            update_job_status(db, job_id, JobStatusEnum.FAILED, error_message=error_message)
            return False

    except Exception as e:
        error_message = f"Erro ao gerar o vídeo com o serviço de vídeo: {str(e)}"
        print(error_message)
        update_job_status(db, job_id, JobStatusEnum.FAILED, error_message=error_message)
        return False

def poll_video_processing_status(db: Session, job_id: int) -> bool:
    """
    NÃO MAIS NECESSÁRIO COM A NOVA APROXIMAÇÃO - Processamento é síncrono agora
    Esta função agora apenas faz upload para o Google Drive após geração síncrona do vídeo
    """
    # Obter o job pelo ID
    job = db.query(PipelineJob).filter(PipelineJob.id == job_id).first()
    if not job:
        print(f"Job com ID {job_id} não encontrado")
        return False

    # Verificar se o status atual é PROCESSING_VIDEO
    if job.status != JobStatusEnum.PROCESSING_VIDEO:
        print(f"Job com ID {job_id} não está no status PROCESSING_VIDEO, atual: {job.status.value}")
        return False

    # Na nova abordagem, o vídeo já está pronto, então vamos fazer upload para o Google Drive
    # Como o vídeo já foi gerado, podemos fazer o upload diretamente
    success = upload_latest_generated_video_to_drive(db, job_id)
    if success:
        print(f"Vídeo gerado e enviado ao Drive com sucesso. Job ID: {job_id}, Status: COMPLETED")
        return True
    else:
        # Em caso de falha no upload para o Drive, atualiza status para FAILED
        error_message = "Falha ao fazer upload do vídeo para o Google Drive"
        update_job_status(db, job_id, JobStatusEnum.FAILED, error_message=error_message)
        return False


def upload_latest_generated_video_to_drive(db: Session, job_id: int) -> bool:
    """
    Faz upload do vídeo recém-gerado para o Google Drive (nova abordagem)
    
    Args:
        db: Sessão do banco de dados
        job_id: ID do job que contém o vídeo a ser enviado

    Returns:
        True se o upload foi feito com sucesso e o job está COMPLETED, False caso contrário
    """
    # Obter o job pelo ID
    job = db.query(PipelineJob).filter(PipelineJob.id == job_id).first()
    if not job:
        print(f"Job com ID {job_id} não encontrado")
        return False

    # Verificar se o status atual é PROCESSING_VIDEO (antes do upload)
    if job.status != JobStatusEnum.PROCESSING_VIDEO:
        print(f"Job com ID {job_id} não está no status PROCESSING_VIDEO, atual: {job.status.value}")
        return False

    # Inicializar o serviço do Google Drive
    try:
        drive_service = DriveService()
    except Exception as e:
        error_message = f"Erro ao inicializar o serviço do Google Drive: {str(e)}"
        update_job_status(db, job_id, JobStatusEnum.FAILED, error_message=error_message)
        return False

    # Gerar nome do arquivo baseado no job e campanha
    campaign = db.query(Campaign).filter(Campaign.id == job.campaign_id).first()
    if not campaign:
        error_message = f"Campanha não encontrada para o job {job.id}"
        update_job_status(db, job_id, JobStatusEnum.FAILED, error_message=error_message)
        return False

    # Criar nome do arquivo
    filename = f"video_{campaign.name.replace(' ', '_')}_job-{job_id}.mp4"

    # Para a nova abordagem, precisamos implementar a lógica para encontrar o vídeo gerado
    # Isso dependerá de como o serviço de vídeo retorna o caminho do vídeo
    # Por enquanto, simularemos chamando novamente o serviço para garantir que o vídeo foi gerado
    try:
        result = generate_video_from_prompt(job.prompt, campaign_id=job.campaign_id)
        if result and result.get("status") == "success":
            video_path = result.get("video_path")
            if not video_path or not os.path.exists(video_path):
                error_message = f"Arquivo de vídeo não encontrado: {video_path}"
                update_job_status(db, job_id, JobStatusEnum.FAILED, error_message=error_message)
                return False

            # Ler o conteúdo do vídeo
            with open(video_path, 'rb') as video_file:
                video_bytes = video_file.read()

            # Fazer upload do vídeo para o Google Drive
            file_metadata = drive_service.upload_file(video_bytes, filename, "video/mp4")
            drive_video_url = file_metadata.get('webViewLink', '')
            
            # Atualizar o job com o link do vídeo no Drive e mudar o status para COMPLETED
            update_job_status(db, job_id, JobStatusEnum.COMPLETED, video_url=drive_video_url)
            print(f"Vídeo enviado para o Google Drive com sucesso. Job ID: {job_id}, Status: COMPLETED")
            return True
        else:
            error_message = result.get("error", "Erro desconhecido na geração do vídeo") if result else "Falha desconhecida na geração do vídeo"
            update_job_status(db, job_id, JobStatusEnum.FAILED, error_message=error_message)
            return False

    except Exception as e:
        error_message = f"Erro ao fazer upload do vídeo para o Google Drive: {str(e)}"
        print(error_message)
        print("Tentando armazenar vídeo temporariamente...")
        
        # Implementar armazenamento temporário em caso de falha de upload
        # (mesma lógica de store_video_temporarily do código original)
        try:
            # Tentar gerar o vídeo novamente para ter os bytes
            result = generate_video_from_prompt(job.prompt, campaign_id=job.campaign_id)
            if result and result.get("status") == "success":
                video_path = result.get("video_path")
                if video_path and os.path.exists(video_path):
                    with open(video_path, 'rb') as video_file:
                        video_bytes = video_file.read()
                    
                    temp_storage_success = store_video_temporarily(video_bytes, job_id, filename)
                    if temp_storage_success:
                        update_job_status(db, job_id, JobStatusEnum.UPLOAD_FAILED, video_url="", error_message=error_message)
                        print(f"Vídeo armazenado temporariamente. Job ID: {job_id}, Status: UPLOAD_FAILED")
                        return False
                    else:
                        # Se nem o armazenamento temporário funcionar, marcar como falha definitiva
                        update_job_status(db, job_id, JobStatusEnum.FAILED, error_message=error_message)
                        print(f"Falha definitiva no armazenamento. Job ID: {job_id}, Status: FAILED")
                        return False
                else:
                    # Arquivo de vídeo não existe
                    update_job_status(db, job_id, JobStatusEnum.FAILED, error_message=error_message)
                    return False
            else:
                # Falha ao tentar gerar o vídeo novamente
                update_job_status(db, job_id, JobStatusEnum.FAILED, error_message=error_message)
                return False
        except Exception as temp_e:
            print(f"Erro adicional ao tentar armazenar temporariamente: {str(temp_e)}")
            update_job_status(db, job_id, JobStatusEnum.FAILED, error_message=error_message)
            return False

def upload_video_to_drive(db: Session, job_id: int, video_url: str) -> bool:
    """
    LEGACY FUNCTION - Mantida para compatibilidade, mas não utilizada na nova abordagem
    Integrar `drive_service.py` com upload do vídeo gerado para Google Drive
    
    Args:
        db: Sessão do banco de dados
        job_id: ID do job que contém o vídeo a ser enviado
        video_url: URL do vídeo gerado que será baixado e enviado para o Google Drive

    Returns:
        True se o upload foi feito com sucesso e o job está COMPLETED, False caso contrário
    """
    print("Função legada chamada. Na nova abordagem, use upload_latest_generated_video_to_drive.")
    return False

def store_video_temporarily(video_bytes: bytes, job_id: int, original_filename: str) -> bool:
    """
    Armazenar vídeo temporariamente em caso de falha no upload para o Google Drive.
    
    Args:
        video_bytes: Conteúdo do vídeo em bytes
        job_id: ID do job relacionado
        original_filename: Nome original do arquivo
        
    Returns:
        True se o armazenamento temporário foi bem-sucedido, False caso contrário
    """
    try:
        # Criar um diretório temporário para armazenamento local
        temp_dir = os.path.join(tempfile.gettempdir(), "video_ugc_pipeline")
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        # Gerar um nome único para o arquivo temporário
        unique_filename = f"temp_{job_id}_{uuid.uuid4()}_{original_filename}"
        temp_file_path = os.path.join(temp_dir, unique_filename)
        
        # Salvar o vídeo nos arquivos temporários do sistema
        with open(temp_file_path, 'wb') as temp_file:
            temp_file.write(video_bytes)
        
        print(f"Vídeo armazenado temporariamente em: {temp_file_path}")
        return True
    except Exception as e:
        print(f"Erro ao armazenar vídeo temporariamente: {str(e)}")
        return False


def handle_http_503_with_retry(func, *args, max_retries=settings.MAX_RETRIES, **kwargs):
    """
    Tratar respostas HTTP 503 (Cold Start) com retentativa
    
    Wrapper para funções que fazem chamadas HTTP que podem retornar 503 (Cold Start)
    e precisam ser repetidas com backoff exponencial.
    
    Args:
        func: função que faz chamada HTTP
        *args: argumentos posicionais para a função
        max_retries: número máximo de tentativas
        **kwargs: argumentos nomeados para a função
        
    Returns:
        Resultado da função ou None se todas as tentativas falharem
    """
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            result = func(*args, **kwargs)
            
            # Verificar se é uma resposta HTTP
            if hasattr(result, 'status_code') and result.status_code == 503:
                retry_count += 1
                wait_time = 2 ** retry_count  # Backoff exponencial
                print(f"Recebido 503 (Cold Start), tentando novamente em {wait_time} segundos...")
                time.sleep(wait_time)
                continue
            else:
                # Se não for 503, retornar o resultado
                return result
        except requests.exceptions.ConnectionError as e:
            if "503" in str(e):
                retry_count += 1
                wait_time = 2 ** retry_count  # Backoff exponencial
                print(f"Conexão retornou 503 (Cold Start), tentando novamente em {wait_time} segundos...")
                time.sleep(wait_time)
                continue
            else:
                # Não é um erro 503, então lançar novamente
                raise e
        except Exception as e:
            # Qualquer outro erro, lançar novamente
            raise e
    
    # Se chegarmos aqui, todas as tentativas falharam
    print(f"Falha após {max_retries} tentativas devido a respostas 503 (Cold Start)")
    return None