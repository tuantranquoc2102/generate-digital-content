import os, json, uuid
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi import Depends
from typing import List
from apps.backend.core.db import SessionLocal, engine, Base
from apps.backend.models.transcription import TranscriptionJob, TranscriptionDetail, TranscriptionImage, JobStatus, ImageType, Transcription
from apps.backend.models.channel_crawler import ChannelCrawler, ChannelCrawlerStatus
from apps.backend.schemas import (
  PresignIn, 
  PresignOut, 
  TranscriptionIn,
  TranscriptionOut,
  TranscriptionJobIn,
  TranscriptionJobOut,
  TranscriptionDetailIn,
  TranscriptionDetailOut,
  TranscriptionImageIn,
  TranscriptionImageOut,
  TranscriptionFullOut,
  YouTubeTranscriptionIn,
  YouTubeTranscriptionOut)
from apps.backend.schemas.channel import ChannelCrawlerIn, ChannelCrawlerOut
from apps.backend.services.storage import presign_put
from apps.backend.services.redis_queue import q   # <- lấy q từ redis_queue

API_CORS = os.getenv("API_CORS_ORIGINS","http://localhost:3000").split(",")

app = FastAPI(title="any2text API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
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
            title=getattr(t, 'title', None),
            created_at=t.created_at,
            language=t.language,
            engine=t.engine
        ))
    
    return results

@app.get("/transcriptions/{tid}", response_model=TranscriptionOut)
def get_transcription(tid: str, db: Session = Depends(get_db)):
    t = db.get(TranscriptionJob, tid)
    if not t: raise HTTPException(404, "Not found")
    
    # Get result from transcription detail
    result = None
    if t.transcription_detail and t.transcription_detail.result_json:
        result = json.loads(t.transcription_detail.result_json)
        
    return TranscriptionOut(
        id=t.id, 
        status=t.status.value, 
        result=result, 
        error=t.error,
        file_url=t.file_url,
        file_key=t.file_key,
        engine=t.engine,
        language=t.language,
        youtube_url=t.youtube_url,
        title=t.title,
        duration=t.duration,
        channel_crawler_id=t.channel_crawler_id,
        created_at=t.created_at,
        updated_at=t.updated_at
    )

@app.post("/youtube/transcriptions", response_model=YouTubeTranscriptionOut)
def create_youtube_transcription(body: YouTubeTranscriptionIn, db: Session = Depends(get_db)):
    tid = str(uuid.uuid4())
    
    # Tạo job với YouTube URL, file sẽ được download trong worker
    t = TranscriptionJob(
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
    
    # enqueue worker cho YouTube preparation (download + upload), sau đó auto-trigger transcription
    q.enqueue("apps.backend.worker.prepare_youtube_job", tid, job_timeout=7200)
    
    return YouTubeTranscriptionOut(
        id=tid,
        status="queued",
        youtube_url=body.youtube_url,
        result=None,
        error=None,
        file_url="",
        file_key=t.file_key
    )

@app.post("/channel/crawler", response_model=ChannelCrawlerOut)
def crawl_channel(body: ChannelCrawlerIn, db: Session = Depends(get_db)):
    """Crawl all videos from a YouTube channel and create transcription jobs"""
    crawler_id = str(uuid.uuid4())
    
    # Create channel crawler record
    crawler = ChannelCrawler(
        id=crawler_id,
        status=ChannelCrawlerStatus.queued,
        channel_url=body.channel_url,
        language=body.language,
        engine=body.engine,
        max_videos=body.max_videos,
        video_type=body.video_type
    )
    db.add(crawler)
    db.commit()
    db.refresh(crawler)
    
    # Enqueue channel crawler job với timeout 1 hour
    q.enqueue("apps.backend.worker.crawl_channel_job", crawler_id, job_timeout=3600)
    
    return ChannelCrawlerOut(
        channel_crawler_id=crawler_id,
        status="queued",
        channel_url=body.channel_url,
        total_videos_found=0,
        total_jobs_created=0,
        jobs=[],
        error=None
    )

@app.get("/channel/crawler/{crawler_id}", response_model=ChannelCrawlerOut)
def get_channel_crawler(crawler_id: str, db: Session = Depends(get_db)):
    """Get channel crawler status and results"""
    crawler = db.query(ChannelCrawler).filter(ChannelCrawler.id == crawler_id).first()
    if not crawler:
        raise HTTPException(404, "Channel crawler not found")
    
    # Get transcription jobs for this crawler
    jobs = []
    transcriptions = db.query(Transcription).filter(Transcription.channel_crawler_id == crawler_id).all()
    for t in transcriptions:
        jobs.append({
            "job_id": t.id,
            "video_url": t.youtube_url or "",
            "title": t.title or "Unknown",
            "status": t.status.value
        })
    
    return ChannelCrawlerOut(
        channel_crawler_id=crawler.id,
        status=crawler.status.value,
        channel_url=crawler.channel_url,
        total_videos_found=crawler.total_videos_found,
        total_jobs_created=crawler.total_jobs_created,
        jobs=jobs,
        error=crawler.error
    )


# =============================================================================
# NEW TRANSCRIPTION DETAIL & IMAGE ENDPOINTS
# =============================================================================

@app.get("/transcriptions/{job_id}/detail", response_model=TranscriptionDetailOut)
def get_transcription_detail(job_id: str, db: Session = Depends(get_db)):
    """Get transcription detail for a job"""
    job = db.get(TranscriptionJob, job_id)
    if not job:
        raise HTTPException(404, "Transcription job not found")
    
    if not job.transcription_detail:
        raise HTTPException(404, "Transcription detail not found")
    
    return TranscriptionDetailOut(
        id=job.transcription_detail.id,
        job_id=job.transcription_detail.job_id,
        result_json=job.transcription_detail.result_json,
        formatted_text=job.transcription_detail.formatted_text,
        summary=job.transcription_detail.summary,
        keywords=job.transcription_detail.keywords,
        processing_time=job.transcription_detail.processing_time,
        word_count=job.transcription_detail.word_count,
        confidence_score=job.transcription_detail.confidence_score,
        created_at=job.transcription_detail.created_at,
        updated_at=job.transcription_detail.updated_at
    )


@app.post("/transcriptions/{job_id}/detail", response_model=TranscriptionDetailOut)
def update_transcription_detail(
    job_id: str, 
    body: TranscriptionDetailIn, 
    db: Session = Depends(get_db)
):
    """Create or update transcription detail"""
    job = db.get(TranscriptionJob, job_id)
    if not job:
        raise HTTPException(404, "Transcription job not found")
    
    # Check if detail already exists
    if job.transcription_detail:
        # Update existing detail
        detail = job.transcription_detail
        if body.result_json is not None:
            detail.result_json = body.result_json
        if body.formatted_text is not None:
            detail.formatted_text = body.formatted_text
        if body.summary is not None:
            detail.summary = body.summary
        if body.keywords is not None:
            detail.keywords = body.keywords
    else:
        # Create new detail
        detail = TranscriptionDetail(
            id=str(uuid.uuid4()),
            job_id=job_id,
            result_json=body.result_json,
            formatted_text=body.formatted_text,
            summary=body.summary,
            keywords=body.keywords
        )
        db.add(detail)
    
    db.commit()
    db.refresh(detail)
    return detail


@app.get("/transcriptions/{job_id}/images", response_model=List[TranscriptionImageOut])
def get_transcription_images(job_id: str, db: Session = Depends(get_db)):
    """Get all images for a transcription job"""
    job = db.get(TranscriptionJob, job_id)
    if not job:
        raise HTTPException(404, "Transcription job not found")
    
    return [TranscriptionImageOut(
        id=img.id,
        job_id=img.job_id,
        image_type=img.image_type.value,
        file_key=img.file_key,
        file_url=img.file_url,
        filename=img.filename,
        mime_type=img.mime_type,
        file_size=img.file_size,
        width=img.width,
        height=img.height,
        description=img.description,
        created_at=img.created_at,
        updated_at=img.updated_at
    ) for img in job.images]


@app.post("/transcriptions/{job_id}/images", response_model=TranscriptionImageOut)
def add_transcription_image(
    job_id: str, 
    body: TranscriptionImageIn, 
    db: Session = Depends(get_db)
):
    """Add an image to a transcription job"""
    job = db.get(TranscriptionJob, job_id)
    if not job:
        raise HTTPException(404, "Transcription job not found")
    
    # Validate image_type
    try:
        image_type_enum = ImageType(body.image_type)
    except ValueError:
        raise HTTPException(400, f"Invalid image_type. Must be one of: {[t.value for t in ImageType]}")
    
    image = TranscriptionImage(
        id=str(uuid.uuid4()),
        job_id=job_id,
        image_type=image_type_enum,
        file_key=body.file_key,
        file_url=body.file_url,
        filename=body.filename,
        mime_type=body.mime_type,
        description=body.description
    )
    
    db.add(image)
    db.commit()
    db.refresh(image)
    return image


@app.get("/transcriptions/{job_id}/full", response_model=TranscriptionFullOut)
def get_transcription_full(job_id: str, db: Session = Depends(get_db)):
    """Get full transcription data including job, detail and images"""
    job = db.get(TranscriptionJob, job_id)
    if not job:
        raise HTTPException(404, "Transcription job not found")
    
    # Build job response
    job_out = TranscriptionJobOut(
        id=job.id,
        status=job.status.value,
        file_key=job.file_key,
        engine=job.engine,
        language=job.language,
        file_url=job.file_url,
        error=job.error,
        youtube_url=job.youtube_url,
        title=job.title,
        duration=job.duration,
        channel_crawler_id=job.channel_crawler_id,
        created_at=job.created_at,
        updated_at=job.updated_at
    )
    
    # Build detail response
    detail_out = None
    if job.transcription_detail:
        detail_out = TranscriptionDetailOut(
            id=job.transcription_detail.id,
            job_id=job.transcription_detail.job_id,
            result_json=job.transcription_detail.result_json,
            formatted_text=job.transcription_detail.formatted_text,
            summary=job.transcription_detail.summary,
            keywords=job.transcription_detail.keywords,
            processing_time=job.transcription_detail.processing_time,
            word_count=job.transcription_detail.word_count,
            confidence_score=job.transcription_detail.confidence_score,
            created_at=job.transcription_detail.created_at,
            updated_at=job.transcription_detail.updated_at
        )
    
    # Build images response
    images_out = [TranscriptionImageOut(
        id=img.id,
        job_id=img.job_id,
        image_type=img.image_type.value,
        file_key=img.file_key,
        file_url=img.file_url,
        filename=img.filename,
        mime_type=img.mime_type,
        file_size=img.file_size,
        width=img.width,
        height=img.height,
        description=img.description,
        created_at=img.created_at,
        updated_at=img.updated_at
    ) for img in job.images]
    
    return TranscriptionFullOut(
        job=job_out,
        detail=detail_out,
        images=images_out
    )
