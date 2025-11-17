import time, json, os
import boto3
from redis import Redis
import requests
from rq import Worker, Queue, Connection
from apps.backend.services.redis_queue import redis_conn
from sqlalchemy.orm import Session
from apps.backend.core.db import SessionLocal, engine, Base
from apps.backend.models.transcription import Transcription, JobStatus
from apps.backend.utils.utils import pack_result
from apps.backend.services.youtube import download_youtube_audio
from faster_whisper import WhisperModel

# Load model once when worker starts
model = WhisperModel("small.en", device="cpu")

# S3/MinIO configuration
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://localhost:9000")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "minioadmin")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "minioadmin")
S3_REGION = os.getenv("S3_REGION", "us-east-1")

def s3_client():
  return boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    region_name=S3_REGION
  )

# Function to download file from URL (MinIO/S3) to local
def download_from_s3(url, out_path):
    """Tải audio từ MinIO/URL về local."""
    r = requests.get(url)
    r.raise_for_status()
    with open(out_path, "wb") as f:
        f.write(r.content)
    return out_path

def transcribe_job(transcription_id: str):
    db: Session = SessionLocal()
    job = None

    try:
        job = db.get(Transcription, transcription_id)
        if not job:
            return

        job.status = JobStatus.processing
        db.commit()

        # Tải audio từ MinIO về /tmp/ 
        audio_path = f"/tmp/{job.id}.mp3"
        # Download file từ S3/MinIO sử dụng boto3 thay vì HTTP URL
        client = s3_client()
        bucket = os.getenv('S3_BUCKET', 'uploads')
        print(f"Downloading from bucket: {bucket}, key: {job.file_key}")
        client.download_file(bucket, job.file_key, audio_path)

        # Chạy Faster-Whisper trên CPU
        segments, info = model.transcribe(audio_path, beam_size=5)
        text = ""
        seg_list = []

        for seg in segments:
            text += seg.text + " "
            seg_list.append({
                "id": seg.id,
                "start": seg.start,
                "end": seg.end,
                "text": seg.text
            })

        # Lưu kết quả vào DB
        job.result_json = pack_result(text=text.strip(), segments=seg_list, language=info.language)
        job.status = JobStatus.done
        db.commit()

        # Xóa file tạm
        os.remove(audio_path)

    except Exception as e:
        if job:
            job.status = JobStatus.error
            job.error = str(e)
            db.commit()

    finally:
        db.close()

def transcribe_youtube_job(transcription_id: str):
    """Process YouTube transcription job"""
    db: Session = SessionLocal()
    job = None

    try:
        job = db.get(Transcription, transcription_id)
        if not job:
            return

        job.status = JobStatus.processing
        db.commit()

        # Download audio từ YouTube
        print(f"Downloading YouTube audio from: {job.youtube_url}")
        audio_path, video_title = download_youtube_audio(job.youtube_url)
        
        # Update job với title
        job.title = video_title
        
        # Upload audio file lên MinIO
        client = s3_client()
        bucket = os.getenv('S3_BUCKET', 'uploads')
        file_key = f"youtube/{job.id}.mp3"
        
        print(f"Uploading to MinIO: {bucket}/{file_key}")
        client.upload_file(audio_path, bucket, file_key)
        
        # Update job với file info
        job.file_key = file_key
        job.file_url = f"{os.getenv('S3_PUBLIC_ENDPOINT', 'http://localhost:9000')}/{bucket}/{file_key}"
        db.commit()

        # Transcribe audio với faster-whisper
        print(f"Transcribing audio: {audio_path}")
        segments, info = model.transcribe(audio_path, beam_size=5)
        text = ""
        seg_list = []

        for seg in segments:
            text += seg.text + " "
            seg_list.append({
                "id": seg.id,
                "start": seg.start,
                "end": seg.end,
                "text": seg.text
            })

        # Lưu kết quả vào DB
        job.result_json = pack_result(text=text.strip(), segments=seg_list, language=info.language)
        job.status = JobStatus.done
        db.commit()

        # Cleanup local file
        os.remove(audio_path)
        print(f"✅ YouTube transcription completed for: {video_title}")

    except Exception as e:
        print(f"❌ YouTube transcription error: {e}")
        if job:
            job.status = JobStatus.error
            job.error = str(e)
            db.commit()

    finally:
        db.close()

# Ensure tables exist in worker too (first run)
Base.metadata.create_all(bind=engine)

# def transcribe_job(transcription_id: str):
#     # fake processing job — replace by faster-whisper / SaaS call
#     db: Session = SessionLocal()
#     try:
#         job = db.get(Transcription, transcription_id)
#         if not job: return
#         job.status = JobStatus.processing
#         db.commit()
#         # simulate heavy work
#         time.sleep(3)
#         # put your real inference here
#         text = "This is a demo transcript generated by the skeleton."
#         job.result_json = pack_result(text)
#         job.status = JobStatus.done
#         db.commit()
#     except Exception as e:
#         if job:
#             job.status = JobStatus.error
#             job.error = str(e)
#             db.commit()
#     finally:
#         db.close()

if __name__ == "__main__":
    listen = ["transcribe"]
    with Connection(Redis(host=os.getenv("REDIS_HOST","redis"), port=int(os.getenv("REDIS_PORT","6379")))):
        worker = Worker([Queue(n) for n in listen])
        worker.work()
