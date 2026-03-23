from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum

from database import Base  # Corrigindo o caminho de importação para o Base do database.py


class JobStatusEnum(Enum):
    PENDING = "PENDING"
    PROMPT_GENERATED = "PROMPT_GENERATED"
    PROCESSING_VIDEO = "PROCESSING_VIDEO"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    briefing_text = Column(Text, nullable=False)  # Length validation will be handled by the application layer
    status = Column(String(50), default="draft")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship with PipelineJob
    jobs = relationship("PipelineJob", back_populates="campaign")

    # Validate briefing_text length (min 50, max 2000) - will be enforced at application level
    def __setattr__(self, name, value):
        if name == "briefing_text":
            if len(value) < 50 or len(value) > 2000:
                raise ValueError("Briefing text must be between 50 and 2000 characters")
        super().__setattr__(name, value)


class PipelineJob(Base):
    __tablename__ = "pipeline_jobs"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    prompt = Column(Text)
    video_url = Column(String(500))
    status = Column(SQLEnum(JobStatusEnum), default=JobStatusEnum.PENDING)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship with Campaign
    campaign = relationship("Campaign", back_populates="jobs")