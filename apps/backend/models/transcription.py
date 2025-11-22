# Transcription models - Import from separate files

from .transcription_job import TranscriptionJob, JobStatus
from .transcription_detail import TranscriptionDetail
from .transcription_image import TranscriptionImage, ImageType

# Backward compatibility alias
Transcription = TranscriptionJob

# Export all for easy imports
__all__ = [
    'TranscriptionJob',
    'TranscriptionDetail', 
    'TranscriptionImage',
    'JobStatus',
    'ImageType',
    'Transcription'  # Backward compatibility
]
