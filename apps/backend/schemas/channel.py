from pydantic import BaseModel
from typing import Optional, List

class ChannelCrawlerIn(BaseModel):
    channel_url: str
    language: str = "auto"
    engine: str = "local"
    max_videos: int = 50  # Giới hạn số video để tránh quá tải
    video_type: str = "shorts"  # "shorts", "videos", "all"

class ChannelJobOut(BaseModel):
    job_id: str
    video_url: str
    title: str
    status: str
    
class ChannelCrawlerOut(BaseModel):
    channel_crawler_id: str
    status: str
    channel_url: str
    total_videos_found: int
    total_jobs_created: int
    jobs: List[ChannelJobOut]
    error: Optional[str] = None