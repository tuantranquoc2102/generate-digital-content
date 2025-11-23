import enum

class JobStatus(str, enum.Enum):
    queued = "queued"
    processing = "processing"
    done = "done"
    error = "error"

class ImageType(str, enum.Enum):
    uploaded="uploaded"
    generated="generated"
    thumbnail="thumbnail"
    screenshot="screenshot"