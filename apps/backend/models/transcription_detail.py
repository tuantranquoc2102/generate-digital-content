# TranscriptionDetail model

from sqlalchemy import String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.sql import func
from apps.backend.core.db import Base


class TranscriptionDetail(Base):
    """
    Chứa nội dung transcription thực tế
    """
    __tablename__ = "transcription_details"
    
    id = mapped_column(String, primary_key=True)
    job_id = mapped_column(String, ForeignKey("transcription_jobs.id"), nullable=False, unique=True)
    
    # Transcription content
    result_json = mapped_column(Text, nullable=True)     # Raw transcription result
    formatted_text = mapped_column(Text, nullable=True) # Clean formatted text
    summary = mapped_column(Text, nullable=True)        # AI generated summary
    keywords = mapped_column(Text, nullable=True)       # Extracted keywords (JSON array)
    
    # Processing metadata
    processing_time = mapped_column(Integer, nullable=True)  # Processing time in seconds
    word_count = mapped_column(Integer, nullable=True)       # Total word count
    confidence_score = mapped_column(String, nullable=True)  # Average confidence
    
    # Relationship
    job = relationship("TranscriptionJob", back_populates="transcription_detail")
    
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())