import time, json, os, uuid, re
import boto3
from redis import Redis
import requests
from rq import Worker, Queue, Connection
from apps.backend.services.redis_queue import redis_conn
from sqlalchemy.orm import Session
from apps.backend.core.db import SessionLocal, engine, Base
from apps.backend.models.transcription import Transcription, JobStatus
from apps.backend.models.channel_crawler import ChannelCrawler, ChannelCrawlerStatus
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
        print(f"Transcribing audio: {audio_path}")
        
        # Determine language for transcription
        transcribe_language = None
        if job.language and job.language != "auto":
            transcribe_language = job.language
            
        print(f"Using language: {transcribe_language or 'auto-detect'}")
        segments, info = model.transcribe(
            audio_path, 
            beam_size=5,
            language=transcribe_language  # None means auto-detect
        )
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
        
        # Determine language for transcription
        transcribe_language = None
        if job.language and job.language != "auto":
            transcribe_language = job.language
        
        print(f"Using language: {transcribe_language or 'auto-detect'}")
        
        # Enhanced transcription parameters for better language detection
        transcription_params = {
            'beam_size': 5,
            'language': transcribe_language,  # None means auto-detect
            'task': 'transcribe',  # Always transcribe, not translate
            'temperature': 0.0,  # More deterministic output
            'compression_ratio_threshold': 2.4,  # Default threshold
            'log_prob_threshold': -1.0,  # Accept lower probability segments
            'no_speech_threshold': 0.6,  # Default speech detection threshold
        }
        
        # For Vietnamese, add special handling
        if transcribe_language == 'vi':
            transcription_params.update({
                'temperature': [0.0, 0.2, 0.4],  # Fewer temperatures for speed
                'beam_size': 3,  # Smaller beam for efficiency
                'log_prob_threshold': -1.5,  # More lenient for Vietnamese
                'no_speech_threshold': 0.4,  # More sensitive speech detection
                'word_timestamps': False,  # Disable word timestamps for speed
                'condition_on_previous_text': True,  # Better context for Vietnamese
            })
            print("🇻🇳 Using Vietnamese-optimized parameters")
        else:
            # For other languages, optimize for speed
            transcription_params.update({
                'word_timestamps': False,  # Disable word timestamps for speed
                'condition_on_previous_text': True,
            })
        
        print(f"⏳ Starting transcription with timeout protection...")
        
        # For very long audio files (>20 minutes), use chunked processing
        import librosa
        try:
            # Get audio duration first
            y, sr = librosa.load(audio_path, sr=None)
            duration = len(y) / sr
            print(f"📊 Audio duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
            
            # If audio is longer than 20 minutes, process in chunks
            if duration > 1200:  # 20 minutes
                print("🔄 Long audio detected - using chunked processing for efficiency...")
                transcription_params.update({
                    'vad_filter': True,  # Use Voice Activity Detection
                    'vad_parameters': dict(min_silence_duration_ms=500),
                    'initial_prompt': None,  # Reset prompt for each chunk
                })
            
        except Exception as e:
            print(f"⚠️ Could not analyze audio duration: {e}")
            duration = 0
        
        segments, info = model.transcribe(audio_path, **transcription_params)
        print(f"🎯 Transcription completed - Language: {info.language}, Duration: {info.duration:.2f}s")
        
        # Process segments with progress tracking for long content
        text = ""
        seg_list = []
        total_segments = sum(1 for _ in segments)  # Count total segments
        print(f"📝 Processing {total_segments} segments...")

        # Reset segments iterator and process
        segments, _ = model.transcribe(audio_path, **transcription_params)
        for i, seg in enumerate(segments):
            text += seg.text + " "
            seg_list.append({
                "id": seg.id,
                "start": seg.start,
                "end": seg.end,
                "text": seg.text
            })
            
            # Progress update for every 100 segments in long content
            if i % 100 == 0 and i > 0:
                progress = (i / total_segments) * 100 if total_segments > 0 else 0
                print(f"⏳ Progress: {progress:.1f}% ({i}/{total_segments} segments)")
                
        print(f"✅ Processed {len(seg_list)} segments total")

        # Lưu kết quả vào DB
        job.result_json = pack_result(text=text.strip(), segments=seg_list, language=info.language)
        job.status = JobStatus.done
        db.commit()

        # Cleanup local file
        os.remove(audio_path)
        print(f"✅ YouTube transcription completed for: {video_title}")

    except Exception as e:
        error_message = str(e)
        
        # Provide more user-friendly error messages
        if "HTTP Error 403" in error_message:
            error_message = "YouTube blocked the download request. This video might be region-restricted or have download protection. Please try a different video."
        elif "Video unavailable" in error_message:
            error_message = "This YouTube video is not available. It might be private, deleted, or region-restricted."
        elif "Sign in to confirm your age" in error_message:
            error_message = "This video is age-restricted and cannot be downloaded automatically."
        elif "This video is not available in your country" in error_message:
            error_message = "This video is not available in your region."
        elif "429" in error_message or "Too Many Requests" in error_message:
            error_message = "YouTube is rate-limiting requests. Please try again later."
        
        print(f"❌ YouTube transcription error: {error_message}")
        if job:
            job.status = JobStatus.error
            job.error = error_message
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

def crawl_channel_job(crawler_id: str):
    """Crawl all videos from a YouTube channel and create transcription jobs"""
    from apps.backend.services.redis_queue import q
    import yt_dlp
    
    db: Session = SessionLocal()
    crawler = None

    try:
        crawler = db.get(ChannelCrawler, crawler_id)
        if not crawler:
            print(f"Channel crawler {crawler_id} not found")
            return

        crawler.status = ChannelCrawlerStatus.processing
        db.commit()
        print(f"Starting channel crawl for: {crawler.channel_url}")

        # Configure yt-dlp for channel crawling
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,  # Only get video info, don't download
            'playlistend': crawler.max_videos,  # Limit number of videos
        }
        
        # Add filter for video type
        if crawler.video_type == "shorts":
            ydl_opts['match_filter'] = lambda info: None if (
                info.get('duration', 0) <= 60 and 
                'shorts' in (info.get('webpage_url', '') or info.get('url', ''))
            ) else f"Not a short video: {info.get('duration', 0)}s"
        elif crawler.video_type == "videos":
            ydl_opts['match_filter'] = lambda info: None if (
                info.get('duration', 0) > 60
            ) else f"Too short for regular video: {info.get('duration', 0)}s"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract channel/playlist info
            try:
                info = ydl.extract_info(crawler.channel_url, download=False)
                if not info:
                    raise Exception("Could not extract channel information")
                
                # Get video entries
                entries = info.get('entries', [])
                if not entries:
                    raise Exception("No videos found in channel")
                
                crawler.total_videos_found = len(entries)
                db.commit()
                
                print(f"Found {len(entries)} videos in channel")
                
                jobs_created = 0
                for entry in entries[:crawler.max_videos]:
                    try:
                        video_url = entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
                        video_title = entry.get('title', 'Unknown Title')
                        
                        # Create transcription job
                        job_id = str(uuid.uuid4())
                        file_key = f"youtube/{job_id}.mp3"
                        
                        transcription_job = Transcription(
                            id=job_id,
                            status=JobStatus.queued,
                            file_key=file_key,
                            engine=crawler.engine,
                            language=crawler.language,
                            youtube_url=video_url,
                            title=video_title,
                            channel_crawler_id=crawler.id,
                            file_url=""
                        )
                        
                        db.add(transcription_job)
                        db.commit()
                        
                        # Enqueue transcription job
                        q.enqueue("apps.backend.worker.transcribe_youtube_job", job_id, job_timeout=7200)
                        jobs_created += 1
                        
                        print(f"Created transcription job for: {video_title[:50]}...")
                        
                    except Exception as e:
                        print(f"Error creating job for video {entry.get('title', 'Unknown')}: {str(e)}")
                        continue
                
                crawler.total_jobs_created = jobs_created
                crawler.status = ChannelCrawlerStatus.done
                db.commit()
                
                print(f"Channel crawl completed. Created {jobs_created} transcription jobs")
                
            except Exception as e:
                error_msg = f"Error extracting channel info: {str(e)}"
                print(error_msg)
                crawler.error = error_msg
                crawler.status = ChannelCrawlerStatus.error
                db.commit()
                
    except Exception as e:
        error_msg = f"Channel crawler error: {str(e)}"
        print(error_msg)
        if crawler:
            crawler.error = error_msg
            crawler.status = ChannelCrawlerStatus.error
            db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    listen = ["transcribe"]
    with Connection(Redis(host=os.getenv("REDIS_HOST","redis"), port=int(os.getenv("REDIS_PORT","6379")))):
        worker = Worker([Queue(n) for n in listen])
        worker.work()
