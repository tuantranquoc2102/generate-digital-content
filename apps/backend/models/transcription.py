# Endpoint cho transcription

import enum
from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.sql import func
from apps.backend.core.db import Base


class JobStatus(str, enum.Enum):
    queued="queued"
    processing="processing"
    done="done"
    error="error"


class Transcription(Base):
    __tablename__ = "transcriptions"
    id = mapped_column(String, primary_key=True)
    status = mapped_column(Enum(JobStatus), nullable=False, default=JobStatus.queued)
    file_key = mapped_column(String, nullable=False)
    engine = mapped_column(String, nullable=False, default="local")
    language = mapped_column(String, nullable=True)
    result_json = mapped_column(Text, nullable=True)
    file_url = mapped_column(String)   # có thể là path local hoặc tên file trong S3
    error = mapped_column(Text, nullable=True)
    # YouTube fields
    youtube_url = mapped_column(String, nullable=True)  # URL gốc của YouTube video
    title = mapped_column(String, nullable=True)        # Tiêu đề video
    
    # Channel crawler relationship
    channel_crawler_id = mapped_column(String, ForeignKey("channel_crawlers.id"), nullable=True)
    channel_crawler = relationship("ChannelCrawler", back_populates="transcription_jobs")
    
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())
