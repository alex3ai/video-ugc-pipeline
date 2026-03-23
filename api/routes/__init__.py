from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models.pydantic import Campaign as CampaignSchema
from models.entities import Campaign as CampaignEntity, JobStatusEnum, PipelineJob

router = APIRouter()

@router.post("/campaigns/", response_model=dict)
def submit_campaign(campaign: CampaignSchema, db: Session = Depends(get_db)):
    """
    Endpoint para submissão de nova campanha com briefing
    """
    # A validação do briefing_text já está implementada no modelo Pydantic
    # e será automaticamente acionada durante a deserialização do request
    
    try:
        # Criar entidade de campanha no banco de dados
        db_campaign = CampaignEntity(
            name=campaign.name,
            briefing_text=campaign.briefing_text,  # Já foi validado pelo Pydantic
            status=campaign.status.value if campaign.status else "draft"
        )
        
        db.add(db_campaign)
        db.commit()
        db.refresh(db_campaign)
        
        # Inicializar um novo job para processamento
        job = initialize_new_job(db, db_campaign.id)
        
        return {
            "id": db_campaign.id,
            "name": db_campaign.name,
            "status": db_campaign.status,
            "job_id": job.id,
            "message": "Campanha criada com sucesso e job inicializado."
        }
    except ValueError as ve:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar campanha: {str(e)}")


@router.get("/campaigns/", response_model=dict)
def list_campaigns(
    status: Optional[str] = None,
    page: int = 1,
    size: int = 10,
    db: Session = Depends(get_db)
):
    """
    Endpoint para listagem de campanhas e seus jobs
    Permite filtrar por status do job opcionalmente e paginar os resultados
    """
    try:
        # Calcular offset baseado na página e tamanho
        offset = (page - 1) * size
        
        # Query base para contagem total (antes da paginação)
        total_query = db.query(CampaignEntity)
        total_count = total_query.count()
        
        # Query para obter as campanhas com paginação
        campaigns_query = total_query.offset(offset).limit(size)
        campaigns = campaigns_query.all()
        
        result = []
        for campaign in campaigns:
            # Obter os jobs associados a cada campanha
            jobs_query = db.query(campaign.jobs)
            if status:
                # Filtrar jobs por status se o parâmetro for fornecido
                try:
                    status_enum = JobStatusEnum(status.upper())
                    jobs_query = jobs_query.filter(campaign.jobs.any(status=status_enum))
                except ValueError:
                    raise HTTPException(status_code=400, detail=f"Status inválido: {status}. Status válidos: {[e.value for e in JobStatusEnum]}")
            
            jobs = jobs_query.all()
            
            # Se foi aplicado filtro de status e não há jobs correspondentes, pular esta campanha
            if status and not jobs:
                continue
            
            campaign_data = {
                "id": campaign.id,
                "name": campaign.name,
                "status": campaign.status,
                "created_at": campaign.created_at,
                "updated_at": campaign.updated_at,
                "briefing_text": campaign.briefing_text[:100] + "..." if len(campaign.briefing_text) > 100 else campaign.briefing_text,
                "jobs": [
                    {
                        "id": job.id,
                        "status": job.status.value,
                        "created_at": job.created_at,
                        "updated_at": job.updated_at,
                        "video_url": job.video_url
                    } for job in jobs
                ]
            }
            result.append(campaign_data)
            
        # Calcular número total de páginas
        total_pages = (total_count + size - 1) // size
        
        return {
            "data": result,
            "pagination": {
                "current_page": page,
                "size": size,
                "total_items": total_count,
                "total_pages": total_pages
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar campanhas: {str(e)}")


@router.get("/jobs/{job_id}", response_model=dict)
def get_job_details(job_id: int, db: Session = Depends(get_db)):
    """
    Endpoint para obter detalhes de um job específico
    """
    try:
        # Buscar o job pelo ID
        job = db.query(PipelineJob).filter(PipelineJob.id == job_id).first()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job não encontrado")
        
        # Obter também os detalhes da campanha associada
        campaign = db.query(CampaignEntity).filter(CampaignEntity.id == job.campaign_id).first()
        
        return {
            "id": job.id,
            "campaign_id": job.campaign_id,
            "campaign_name": campaign.name if campaign else None,
            "prompt": job.prompt,
            "video_url": job.video_url,
            "status": job.status.value,
            "error_message": job.error_message,
            "created_at": job.created_at,
            "updated_at": job.updated_at
        }
    except HTTPException:
        # Re-raise HTTP exceptions to preserve status codes
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter detalhes do job: {str(e)}")


# Importar outros módulos de rotas para registrar
def include_routes(app):
    app.include_router(router, prefix="/api/v1")