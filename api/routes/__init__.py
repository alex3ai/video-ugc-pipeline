from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models.pydantic import Campaign as CampaignSchema
from models.entities import Campaign as CampaignEntity
from services.job_service import initialize_new_job

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


@router.get("/campaigns/", response_model=list)
def list_campaigns(db: Session = Depends(get_db)):
    """
    Endpoint para listagem de campanhas e seus jobs
    """
    try:
        campaigns = db.query(CampaignEntity).all()
        
        result = []
        for campaign in campaigns:
            # Obter os jobs associados a cada campanha
            jobs = campaign.jobs  # A relação já está definida no modelo
            
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
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar campanhas: {str(e)}")


# Importar outros módulos de rotas para registrar
def include_routes(app):
    app.include_router(router, prefix="/api/v1")