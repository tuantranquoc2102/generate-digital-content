from pydantic import BaseModel
from typing import Optional, Any

class PresignIn(BaseModel):
    filename: str
    contentType: str

class PresignOut(BaseModel):
    uploadUrl: str
    fileKey: str

class CreateTranscriptionIn(BaseModel):
    fileKey: str
    language: Optional[str] = "auto"
    engine: Optional[str] = "local"

class CreateTranscriptionOut(BaseModel):
    id: str
    status: str

class TranscriptionOut(BaseModel):
    id: str
    status: str
    result: Optional[Any] = None
    error: Optional[str] = None
