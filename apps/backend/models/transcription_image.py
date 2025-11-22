# TranscriptionImage model

import enum
from sqlalchemy import String, Text, DateTime, Enum, ForeignKey, Integer
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.sql import func
from apps.backend.core.db import Base


class ImageType(str, enum.Enum):
    uploaded="uploaded"        # User uploaded image
    generated="generated"      # AI generated image
    thumbnail="thumbnail"      # Video thumbnail
    screenshot="screenshot"    # Video screenshot


class TranscriptionImage(Base):
    """
    Lưu trữ hình ảnh liên quan đến transcription
    """
    __tablename__ = "transcription_images"
    
    id = mapped_column(String, primary_key=True)
    job_id = mapped_column(String, ForeignKey("transcription_jobs.id"), nullable=False)
    
    # Image metadata
    image_type = mapped_column(Enum(ImageType), nullable=False)
    file_key = mapped_column(String, nullable=False)     # Storage key/path
    file_url = mapped_column(String, nullable=True)      # Public URL if available
    filename = mapped_column(String, nullable=True)      # Original filename
    mime_type = mapped_column(String, nullable=True)     # image/jpeg, image/png, etc.
    file_size = mapped_column(Integer, nullable=True)    # File size in bytes
    
    # Image properties
    width = mapped_column(Integer, nullable=True)
    height = mapped_column(Integer, nullable=True)
    description = mapped_column(Text, nullable=True)     # AI generated description
    
    # Relationship
    job = relationship("TranscriptionJob", back_populates="images")
    
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())