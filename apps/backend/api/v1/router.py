from fastapi import APIRouter
from apps.backend.api.v1 import transcription, youtube, channel, presign

router = APIRouter()
router.include_router(transcription.router)
router.include_router(youtube.router)
router.include_router(channel.router)
router.include_router(presign.router)