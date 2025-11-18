import os, json, uuid
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi import Depends
from typing import List
from apps.backend.core.db import SessionLocal, engine, Base
from apps.backend.models.transcription import Transcription, JobStatus
from apps.backend.schemas import (
  PresignIn, 
  PresignOut, 
  TranscriptionIn,
  TranscriptionOut,
  YouTubeTranscriptionIn,
  YouTubeTranscriptionOut)
from apps.backend.services.storage import presign_put
from apps.backend.services.redis_queue import q   # <- lấy q từ redis_queue

API_CORS = os.getenv("API_CORS_ORIGINS","http://localhost:3000")

app = FastAPI(title="any2text API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[API_CORS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auto-create tables on API start
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@app.get("/health")
def health(): return {"ok": True}

@app.post("/uploads/presign", response_model=PresignOut)
def presign(body: PresignIn):
    url, key = presign_put(body.file_name, body.content_type)
    return {"upload_url": url, "file_key": key}

@app.post("/transcriptions", response_model=TranscriptionOut)
def create_transcription(body: TranscriptionIn, db: Session = Depends(get_db)):
    tid = str(uuid.uuid4())
    # Tạo file_url từ fileKey cho MinIO - sử dụng public endpoint
    file_url = f"{os.getenv('S3_PUBLIC_ENDPOINT', 'http://localhost:9000')}/{os.getenv('S3_BUCKET', 'uploads')}/{body.fileKey}"
    t = Transcription(
        id=tid, 
        status=JobStatus.queued, 
        file_key=body.fileKey, 
        engine=body.engine or "local",
        language=body.language,
        file_url=file_url
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    # enqueue worker - sử dụng string path để tránh circular import với timeout 2 hours
    q.enqueue("apps.backend.worker.transcribe_job", tid, job_timeout=7200)
    return TranscriptionOut(
        id=tid, 
        status="queued", 
        result=None, 
        error=None,
        file_url=file_url,
        file_key=body.fileKey
    )

@app.get("/transcriptions", response_model=List[TranscriptionOut])
def list_transcriptions(
    limit: int = Query(default=20, le=100, description="Number of items to return"),
    offset: int = Query(default=0, ge=0, description="Number of items to skip"),
    status: str = Query(default=None, description="Filter by status: queued, processing, done, error"),
    db: Session = Depends(get_db)
):
    """Get list of all transcriptions with pagination and filtering"""
    query = db.query(Transcription)
    
    # Filter by status if provided
    if status:
        try:
            status_enum = JobStatus(status)
            query = query.filter(Transcription.status == status_enum)
        except ValueError:
            raise HTTPException(400, f"Invalid status. Must be one of: {[s.value for s in JobStatus]}")
    
    # Order by created_at descending (newest first)
    query = query.order_by(Transcription.created_at.desc())
    
    # Apply pagination
    transcriptions = query.offset(offset).limit(limit).all()
    
    # Convert to response format
    results = []
    for t in transcriptions:
        result = json.loads(t.result_json) if t.result_json else None
        results.append(TranscriptionOut(
            id=t.id,
            status=t.status.value,
            result=result,
            error=t.error,
            file_url=t.file_url,
            file_key=t.file_key,
            youtube_url=getattr(t, 'youtube_url', None),
            title=getattr(t, 'title', None),
            created_at=t.created_at,
            language=t.language,
            engine=t.engine
        ))
    
    return results

@app.get("/transcriptions/{tid}", response_model=TranscriptionOut)
def get_transcription(tid: str, db: Session = Depends(get_db)):
    t = db.get(Transcription, tid)
    if not t: raise HTTPException(404, "Not found")
    result = json.loads(t.result_json) if t.result_json else None
    return TranscriptionOut(
        id=t.id, 
        status=t.status.value, 
        result=result, 
        error=t.error,
        file_url=t.file_url,
        file_key=t.file_key
    )

@app.post("/youtube/transcriptions", response_model=YouTubeTranscriptionOut)
def create_youtube_transcription(body: YouTubeTranscriptionIn, db: Session = Depends(get_db)):
    tid = str(uuid.uuid4())
    
    # Tạo job với YouTube URL, file sẽ được download trong worker
    t = Transcription(
        id=tid,
        status=JobStatus.queued,
        file_key=f"youtube/{tid}.mp3",  # Placeholder cho file key
        engine=body.engine or "local",
        language=body.language,
        youtube_url=body.youtube_url,
        file_url=""  # Sẽ được update sau khi download
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    
    # enqueue worker cho YouTube processing với timeout 2 hours
    q.enqueue("apps.backend.worker.transcribe_youtube_job", tid, job_timeout=7200)
    
    return YouTubeTranscriptionOut(
        id=tid,
        status="queued",
        youtube_url=body.youtube_url,
        result=None,
        error=None,
        file_url="",
        file_key=t.file_key
    )
