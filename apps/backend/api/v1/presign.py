from fastapi import APIRouter
from apps.backend.schemas import PresignIn, PresignOut
from apps.backend.services.storage import presign_put

router = APIRouter()

@router.post("/uploads/presign", response_model=PresignOut)
def presign(body: PresignIn):
    url, key = presign_put(body.file_name, body.content_type)
    return {"upload_url": url, "file_key": key}
