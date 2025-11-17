from pydantic import BaseModel
from typing import Optional

class YouTubeTranscriptionIn(BaseModel):
    youtube_url: str
    engine: str = "local"
    language: Optional[str] = None

class YouTubeTranscriptionOut(BaseModel):
    id: str
    status: str
    youtube_url: str
    title: Optional[str] = None
    result: Optional[dict] = None
    error: Optional[str] = None
    file_url: Optional[str] = None
    file_key: Optional[str] = None