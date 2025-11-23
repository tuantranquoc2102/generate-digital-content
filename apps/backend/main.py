import os, json, uuid
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi import Depends
from typing import List
from apps.backend.core.db import SessionLocal, engine, Base
from apps.backend.models.channel_crawler import ChannelCrawler
from apps.backend.schemas import PresignIn, PresignOut, YouTubeTranscriptionIn, YouTubeTranscriptionOut
from apps.backend.schemas.channel import ChannelCrawlerIn, ChannelCrawlerOut
from apps.backend.services.storage import presign_put
from apps.backend.services.redis_queue import q
from apps.backend.api.api import router as api_router

API_CORS = os.getenv("API_CORS_ORIGINS","http://localhost:3000").split(",")


app = FastAPI(title="any2text API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(api_router, prefix="/api")

# Auto-create tables on API start
Base.metadata.create_all(bind=engine)

@app.get("/health")
def health(): return {"ok": True}