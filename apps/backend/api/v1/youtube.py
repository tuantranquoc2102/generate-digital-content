from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid
from apps.backend.core.db import SessionLocal, get_db, get_db
from apps.backend.models.transcription import Transcription, TranscriptionJob
from apps.backend.models.enums import JobStatus
from apps.backend.schemas import YouTubeTranscriptionIn, YouTubeTranscriptionOut
from apps.backend.services.redis_queue import q
from apps.backend.schemas.channel import ChannelCrawlerIn, ChannelCrawlerOut
from apps.backend.models.channel_crawler import ChannelCrawler


router = APIRouter()

@router.post("/youtube/transcriptions", response_model=YouTubeTranscriptionOut)
def create_youtube_transcription(body: YouTubeTranscriptionIn, db: Session = Depends(get_db)):
    tid = str(uuid.uuid4())
    t = TranscriptionJob(
        id=tid,
        status=JobStatus.queued,
        file_key=f"youtube/{tid}.mp3",
        engine=body.engine or "local",
        language=body.language,
        youtube_url=body.youtube_url,
        file_url=""
    )
    db.add(t)
    db.commit()
    db.refresh(t)
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

@router.post("/channel/crawler", response_model=ChannelCrawlerOut)
def crawl_channel(body: ChannelCrawlerIn, db: Session = Depends(get_db)):
    crawler_id = str(uuid.uuid4())
    crawler = ChannelCrawler(
        id=crawler_id,
        status=JobStatus.queued,
        channel_url=body.channel_url,
        language=body.language,
        engine=body.engine,
        max_videos=body.max_videos,
        video_type=body.video_type
    )
    db.add(crawler)
    db.commit()
    db.refresh(crawler)
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

@router.get("/channel/crawler/{crawler_id}", response_model=ChannelCrawlerOut)
def get_channel_crawler(crawler_id: str, db: Session = Depends(get_db)):
    crawler = db.query(ChannelCrawler).filter(ChannelCrawler.id == crawler_id).first()
    if not crawler:
        raise HTTPException(404, "Channel crawler not found")
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