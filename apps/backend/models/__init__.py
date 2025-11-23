# Models package - Export all models

from .transcription_job import TranscriptionJob, JobStatus
from .transcription_detail import TranscriptionDetail
from .transcription_image import TranscriptionImage, ImageType
from .transcription import Transcription  # Backward compatibility
from .channel_crawler import ChannelCrawler

__all__ = [
    # Transcription models
    'TranscriptionJob',
    'TranscriptionDetail',
    'TranscriptionImage',
    'JobStatus',
    'ImageType',
    'Transcription',  # Backward compatibility
    
    # Channel crawler models
    'ChannelCrawler'
]