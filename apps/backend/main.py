import os, json, uuid
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi import Depends
from typing import List
from apps.backend.core.db import SessionLocal, engine, Base
from apps.backend.models.channel_crawler import ChannelCrawler, ChannelCrawlerStatus
from apps.backend.schemas import PresignIn, PresignOut, YouTubeTranscriptionIn, YouTubeTranscriptionOut
from apps.backend.schemas.channel import ChannelCrawlerIn, ChannelCrawlerOut
from apps.backend.services.storage import presign_put
from apps.backend.services.redis_queue import q
from apps.backend.api.api import router as api_router

API_CORS = os.getenv("API_CORS_ORIGINS","http://localhost:3000").split(",")


app = FastAPI(title="any2text API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(api_router, prefix="/api")

# Auto-create tables on API start
Base.metadata.create_all(bind=engine)

@app.get("/health")
def health(): return {"ok": True}

@app.post("/uploads/presign", response_model=PresignOut)

@app.post("/transcriptions", response_model=TranscriptionOut)
    tid = str(uuid.uuid4())
    # Tạo file_url từ fileKey cho MinIO - sử dụng public endpoint
    file_url = f"{os.getenv('S3_PUBLIC_ENDPOINT', 'http://localhost:9000')}/{os.getenv('S3_BUCKET', 'uploads')}/{body.fileKey}"
    t = TranscriptionJob(
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
        file_key=body.fileKey,
        engine=body.engine or "local",
        language=body.language
    )

@app.get("/transcriptions", response_model=List[TranscriptionOut])
def list_transcriptions(
    limit: int = Query(default=20, le=100, description="Number of items to return"),
    offset: int = Query(default=0, ge=0, description="Number of items to skip"),
    status: str = Query(default=None, description="Filter by status: queued, processing, done, error"),
    db: Session = Depends(get_db)
):
    """Get list of all transcriptions with pagination and filtering"""
    query = db.query(TranscriptionJob)
    
    # Filter by status if provided
    if status:
        try:
            status_enum = JobStatus(status)
            query = query.filter(TranscriptionJob.status == status_enum)
        except ValueError:
            raise HTTPException(400, f"Invalid status. Must be one of: {[s.value for s in JobStatus]}")
    
    # Order by created_at descending (newest first)
    query = query.order_by(TranscriptionJob.created_at.desc())
    
    # Apply pagination
    transcriptions = query.offset(offset).limit(limit).all()
    
    # Convert to response format
    results = []
    for t in transcriptions:
        # Get transcription detail if available
        result = None
        if t.transcription_detail and t.transcription_detail.result_json:
            result = json.loads(t.transcription_detail.result_json)
            
        results.append(TranscriptionOut(
            id=t.id,
            status=t.status.value,
            result=result,
            error=t.error,
            file_url=t.file_url,
            file_key=t.file_key,
            youtube_url=getattr(t, 'youtube_url', None),
    db.refresh(image)
    
    return TranscriptionImageOut(
        id=image.id,
        job_id=image.job_id,
        image_type=image.image_type.value,
        file_key=image.file_key,
        file_url=image.file_url,
        filename=image.filename,
        mime_type=image.mime_type,
        description=image.description,
        created_at=image.created_at
    )

@app.post("/transcriptions/{tid}/format-dialogue")
    """Format transcription as dialogue using OpenAI"""
    from apps.backend.services.openai_service import format_as_dialogue
    
    job = db.get(TranscriptionJob, tid)
    if not job or not job.transcription_detail:
        raise HTTPException(404, "Transcription not found or not completed")
    
    original_text = job.transcription_detail.formatted_text
    if not original_text:
        raise HTTPException(400, "No transcription text available")
    
    try:
        # Queue the OpenAI formatting job
        job_id = f"format_dialogue_{tid}"
        q.enqueue_call(
            func='apps.backend.worker.format_dialogue_job',
            args=[tid, original_text],
            job_id=job_id,
            timeout=300
        )
        
        return {"message": "Dialogue formatting started", "job_id": job_id}
    except Exception as e:
