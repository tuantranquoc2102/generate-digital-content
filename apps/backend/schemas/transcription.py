# schemas/transcription.py - Updated for new structure
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# =============================================================================
# TRANSCRIPTION JOB SCHEMAS
# =============================================================================

class TranscriptionJobIn(BaseModel):
    """Schema for creating a transcription job"""
    fileKey: str
    engine: str = "local"
    language: Optional[str] = None
    youtube_url: Optional[str] = None
    title: Optional[str] = None


class TranscriptionJobOut(BaseModel):
    """Schema for returning transcription job details"""
    id: str
    status: str
    file_key: str
    engine: str
    language: Optional[str] = None
    file_url: Optional[str] = None
    error: Optional[str] = None
    youtube_url: Optional[str] = None
    title: Optional[str] = None
    duration: Optional[int] = None
    channel_crawler_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Backward compatibility fields (for old frontend code)
    result: Optional[dict] = None  # Will be populated from TranscriptionDetail if available


# =============================================================================
# TRANSCRIPTION DETAIL SCHEMAS  
# =============================================================================

class TranscriptionDetailIn(BaseModel):
    """Schema for creating transcription detail"""
    result_json: Optional[str] = None
    formatted_text: Optional[str] = None
    summary: Optional[str] = None
    keywords: Optional[str] = None


class TranscriptionDetailOut(BaseModel):
    """Schema for returning transcription detail"""
    id: str
    job_id: str
    result_json: Optional[str] = None
    formatted_text: Optional[str] = None
    summary: Optional[str] = None
    keywords: Optional[str] = None
    processing_time: Optional[int] = None
    word_count: Optional[int] = None
    confidence_score: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# =============================================================================
# TRANSCRIPTION IMAGE SCHEMAS
# =============================================================================

class TranscriptionImageIn(BaseModel):
    """Schema for creating transcription image"""
    image_type: str  # uploaded, generated, thumbnail, screenshot
    file_key: str
    file_url: Optional[str] = None
    filename: Optional[str] = None
    mime_type: Optional[str] = None
    description: Optional[str] = None


class TranscriptionImageOut(BaseModel):
    """Schema for returning transcription image"""
    id: str
    job_id: str
    image_type: str
    file_key: str
    file_url: Optional[str] = None
    filename: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# =============================================================================
# COMBINED SCHEMAS
# =============================================================================

class TranscriptionFullOut(BaseModel):
    """Schema for returning full transcription with details and images"""
    job: TranscriptionJobOut
    detail: Optional[TranscriptionDetailOut] = None
    images: List[TranscriptionImageOut] = []


# =============================================================================
# BACKWARD COMPATIBILITY
# =============================================================================

# Backward compatibility aliases
TranscriptionIn = TranscriptionJobIn
TranscriptionOut = TranscriptionJobOut