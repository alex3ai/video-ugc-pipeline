from pydantic import BaseModel, validator
from typing import Optional
from enum import Enum


class CampaignStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


class JobStatus(str, Enum):
    PENDING = "PENDING"
    PROMPT_GENERATED = "PROMPT_GENERATED"
    PROCESSING_VIDEO = "PROCESSING_VIDEO"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"


class Campaign(BaseModel):
    """
    Model representing a campaign with a validated briefing text
    """
    name: str
    briefing_text: str
    status: Optional[CampaignStatus] = CampaignStatus.DRAFT

    @validator("briefing_text")
    def validate_briefing_text(cls, v):
        if len(v) < 50 or len(v) > 2000:
            raise ValueError("Briefing text must be between 50 and 2000 characters")
        return v


class PipelineJob(BaseModel):
    """
    Model representing a pipeline job with status tracking
    """
    campaign_id: str
    prompt: Optional[str] = None
    video_url: Optional[str] = None
    status: JobStatus = JobStatus.PENDING
    error_message: Optional[str] = None