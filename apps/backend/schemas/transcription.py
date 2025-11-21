# schemas/transcription.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# Schema for creating a transcription
# Input data
class TranscriptionIn(BaseModel):
    fileKey: str
    engine: str = "local"
    language: Optional[str] = None

# Output data  
# Schema for returning transcription details
class TranscriptionOut(BaseModel):
    id: str
    status: str
    result: Optional[dict] = None
    error: Optional[str] = None
    file_url: Optional[str] = None
    file_key: Optional[str] = None
    title: Optional[str] = None
    created_at: Optional[datetime] = None
    youtube_url: Optional[str] = None
    language: Optional[str] = None
    engine: Optional[str] = None