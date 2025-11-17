from pydantic import BaseModel

class PresignIn(BaseModel):
    file_name: str
    content_type: str

class PresignOut(BaseModel):
    upload_url: str
    file_key: str
