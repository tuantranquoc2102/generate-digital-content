import os, json, uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi import Depends
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
    # enqueue worker - sử dụng string path để tránh circular import
    q.enqueue("apps.backend.worker.transcribe_job", tid)
    return TranscriptionOut(
        id=tid, 
        status="queued", 
        result=None, 
        error=None,
        file_url=file_url,
        file_key=body.fileKey
    )

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
    
    # enqueue worker cho YouTube processing
    q.enqueue("apps.backend.worker.transcribe_youtube_job", tid)
    
    return YouTubeTranscriptionOut(
        id=tid,
        status="queued",
        youtube_url=body.youtube_url,
        result=None,
        error=None,
        file_url="",
        file_key=t.file_key
    )
