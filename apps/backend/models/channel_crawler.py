from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from apps.backend.core.db import Base

class ChannelCrawlerStatus(enum.Enum):
    queued = "queued"
    processing = "processing"
    done = "done" 
    error = "error"

class ChannelCrawler(Base):
    __tablename__ = "channel_crawlers"
    
    id = Column(String, primary_key=True)
    status = Column(Enum(ChannelCrawlerStatus), default=ChannelCrawlerStatus.queued)
    channel_url = Column(String, nullable=False)
    language = Column(String, default="auto")
    engine = Column(String, default="local")
    max_videos = Column(Integer, default=50)
    video_type = Column(String, default="shorts")
    
    total_videos_found = Column(Integer, default=0)
    total_jobs_created = Column(Integer, default=0)
    
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationship to transcription jobs
    transcription_jobs = relationship("Transcription", back_populates="channel_crawler")