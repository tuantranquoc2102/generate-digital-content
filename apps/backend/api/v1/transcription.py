import os, json, uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from apps.backend.core.db import SessionLocal, get_db
from apps.backend.models.transcription import TranscriptionJob, TranscriptionDetail, TranscriptionImage, ImageType
from apps.backend.models.enums import JobStatus
from apps.backend.schemas import (
	TranscriptionIn, TranscriptionOut, TranscriptionDetailIn, TranscriptionDetailOut, TranscriptionImageIn, TranscriptionImageOut, TranscriptionFullOut
)
from apps.backend.schemas.transcription import TranscriptionJobOut
from apps.backend.services.redis_queue import q

router = APIRouter()

@router.post("/transcriptions", response_model=TranscriptionOut)
def create_transcription(body: TranscriptionIn, db: Session = Depends(get_db)):
	tid = str(uuid.uuid4())
	file_url = f"{os.getenv('S3_PUBLIC_ENDPOINT', 'http://localhost:9000')}/{os.getenv('S3_BUCKET', 'uploads')}/{body.fileKey}"
	t = TranscriptionJob(
		id=tid,
		status=JobStatus.queued,
		file_key=body.fileKey,
		engine=body.engine or "local",
		language=body.language,
		file_url=file_url
	)
	db.add(t)
	db.commit()
	db.refresh(t)
	q.enqueue("apps.backend.worker.transcribe_job", tid, job_timeout=7200)
	return TranscriptionOut(
		id=tid,
		status="queued",
		result=None,
		error=None,
		file_url=file_url,
		file_key=body.fileKey,
		engine=body.engine or "local",
		language=body.language
	)

@router.get("/transcriptions", response_model=List[TranscriptionOut])
def list_transcriptions(
	limit: int = Query(default=20, le=100, description="Number of items to return"),
	offset: int = Query(default=0, ge=0, description="Number of items to skip"),
	status: str = Query(default=None, description="Filter by status: queued, processing, done, error"),
	db: Session = Depends(get_db)
):
	query = db.query(TranscriptionJob)
	if status:
		try:
			status_enum = JobStatus(status)
			query = query.filter(TranscriptionJob.status == status_enum)
		except ValueError:
			raise HTTPException(400, f"Invalid status. Must be one of: {[s.value for s in JobStatus]}")
	query = query.order_by(TranscriptionJob.created_at.desc())
	transcriptions = query.offset(offset).limit(limit).all()
	results = []
	for t in transcriptions:
		result = None
		if t.transcription_detail and t.transcription_detail.result_json:
			result = json.loads(t.transcription_detail.result_json)
			results.append(TranscriptionOut(
				id=t.id,
				status=t.status.value,
				result=result,
				error=t.error,
				file_url=t.file_url,
				file_key=t.file_key,
				youtube_url=getattr(t, 'youtube_url', None),
				title=getattr(t, 'title', None),
				created_at=t.created_at,
				language=t.language,
				engine=t.engine
		))
	return results

@router.get("/transcriptions/{tid}", response_model=TranscriptionOut)
def get_transcription(tid: str, db: Session = Depends(get_db)):
	t = db.get(TranscriptionJob, tid)
	if not t:
		raise HTTPException(404, "Not found")
	result = None
	if t.transcription_detail and t.transcription_detail.result_json:
		result = json.loads(t.transcription_detail.result_json)
	return TranscriptionOut(
		id=t.id,
		status=t.status.value,
		result=result,
		error=t.error,
		file_url=t.file_url,
		file_key=t.file_key,
		engine=t.engine,
		language=t.language,
		youtube_url=t.youtube_url,
		title=t.title,
		duration=t.duration,
		channel_crawler_id=t.channel_crawler_id,
		created_at=t.created_at,
		updated_at=t.updated_at
	)

@router.get("/transcriptions/{job_id}/detail", response_model=TranscriptionDetailOut)
def get_transcription_detail(job_id: str, db: Session = Depends(get_db)):
	job = db.get(TranscriptionJob, job_id)
	if not job:
		raise HTTPException(404, "Transcription job not found")
	if not job.transcription_detail:
		raise HTTPException(404, "Transcription detail not found")
	return TranscriptionDetailOut(
		id=job.transcription_detail.id,
		job_id=job.transcription_detail.job_id,
		result_json=job.transcription_detail.result_json,
		formatted_text=job.transcription_detail.formatted_text,
		summary=job.transcription_detail.summary,
		keywords=job.transcription_detail.keywords,
		processing_time=job.transcription_detail.processing_time,
		word_count=job.transcription_detail.word_count,
		confidence_score=job.transcription_detail.confidence_score,
		created_at=job.transcription_detail.created_at,
		updated_at=job.transcription_detail.updated_at
	)

@router.post("/transcriptions/{job_id}/detail", response_model=TranscriptionDetailOut)
def update_transcription_detail(job_id: str, body: TranscriptionDetailIn, db: Session = Depends(get_db)):
	job = db.get(TranscriptionJob, job_id)
	if not job:
		raise HTTPException(404, "Transcription job not found")
	if job.transcription_detail:
		detail = job.transcription_detail
		if body.result_json is not None:
			detail.result_json = body.result_json
		if body.formatted_text is not None:
			detail.formatted_text = body.formatted_text
		if body.summary is not None:
			detail.summary = body.summary
	if body.keywords is not None:
		detail.keywords = body.keywords
	else:
		detail = TranscriptionDetail(
			id=str(uuid.uuid4()),
			job_id=job_id,
			result_json=body.result_json,
			formatted_text=body.formatted_text,
			summary=body.summary,
			keywords=body.keywords
		)
		db.add(detail)
	db.commit()
	db.refresh(detail)
	return detail

@router.get("/transcriptions/{job_id}/images", response_model=List[TranscriptionImageOut])
def get_transcription_images(job_id: str, db: Session = Depends(get_db)):
	job = db.get(TranscriptionJob, job_id)
	if not job:
		raise HTTPException(404, "Transcription job not found")
	return [TranscriptionImageOut(
		id=img.id,
		job_id=img.job_id,
		image_type=img.image_type.value,
		file_key=img.file_key,
		file_url=img.file_url,
		filename=img.filename,
		mime_type=img.mime_type,
		file_size=img.file_size,
		width=img.width,
		height=img.height,
		description=img.description,
		created_at=img.created_at,
		updated_at=img.updated_at
	) for img in job.images]

@router.post("/transcriptions/{job_id}/images", response_model=TranscriptionImageOut)
def add_transcription_image(job_id: str, body: TranscriptionImageIn, db: Session = Depends(get_db)):
	job = db.get(TranscriptionJob, job_id)
	if not job:
		raise HTTPException(404, "Transcription job not found")
	try:
		image_type_enum = ImageType(body.image_type)
	except ValueError:
		raise HTTPException(400, f"Invalid image_type. Must be one of: {[t.value for t in ImageType]}")
	image = TranscriptionImage(
		id=str(uuid.uuid4()),
		job_id=job_id,
		image_type=image_type_enum,
		file_key=body.file_key,
		file_url=body.file_url,
		filename=body.filename,
		mime_type=body.mime_type,
		description=body.description
	)
	db.add(image)
	db.commit()
	db.refresh(image)
	return image

@router.get("/transcriptions/{job_id}/full", response_model=TranscriptionFullOut)
def get_transcription_full(job_id: str, db: Session = Depends(get_db)):
	job = db.get(TranscriptionJob, job_id)
	if not job:
		raise HTTPException(404, "Transcription job not found")
	job_out = TranscriptionJobOut(
		id=job.id,
		status=job.status.value,
		file_key=job.file_key,
		engine=job.engine,
		language=job.language,
		file_url=job.file_url,
		error=job.error,
		youtube_url=job.youtube_url,
		title=job.title,
		duration=job.duration,
		channel_crawler_id=job.channel_crawler_id,
		created_at=job.created_at,
		updated_at=job.updated_at
	)
	detail_out = None
	if job.transcription_detail:
		detail_out = TranscriptionDetailOut(
			id=job.transcription_detail.id,
			job_id=job.transcription_detail.job_id,
			result_json=job.transcription_detail.result_json,
			formatted_text=job.transcription_detail.formatted_text,
			summary=job.transcription_detail.summary,
			keywords=job.transcription_detail.keywords,
			processing_time=job.transcription_detail.processing_time,
			word_count=job.transcription_detail.word_count,
			confidence_score=job.transcription_detail.confidence_score,
			created_at=job.transcription_detail.created_at,
			updated_at=job.transcription_detail.updated_at
		)
	images_out = [TranscriptionImageOut(
		id=img.id,
		job_id=img.job_id,
		image_type=img.image_type.value,
		file_key=img.file_key,
		file_url=img.file_url,
		filename=img.filename,
		mime_type=img.mime_type,
		file_size=img.file_size,
		width=img.width,
		height=img.height,
		description=img.description,
		created_at=img.created_at,
		updated_at=img.updated_at
	) for img in job.images]
	return TranscriptionFullOut(
		job=job_out,
		detail=detail_out,
		images=images_out
	)

@router.post("/transcriptions/{tid}/format-dialogue")
def format_dialogue_with_openai(tid: str, db: Session = Depends(get_db)):
	from apps.backend.services.openai_service import format_as_dialogue
	job = db.get(TranscriptionJob, tid)
	if not job or not job.transcription_detail:
		raise HTTPException(404, "Transcription not found or not completed")
	original_text = job.transcription_detail.formatted_text
	if not original_text:
		raise HTTPException(400, "No transcription text available")
	try:
		job_id = f"format_dialogue_{tid}"
		q.enqueue_call(
			func='apps.backend.worker.format_dialogue_job',
			args=[tid, original_text],
			job_id=job_id,
			timeout=300
		)
		return {"message": "Dialogue formatting started", "job_id": job_id}
	except Exception as e:
		raise HTTPException(500, f"Failed to start dialogue formatting: {str(e)}")

@router.post("/transcriptions/{tid}/generate-image")
def generate_image_for_dialogue(tid: str, prompt: str = None, db: Session = Depends(get_db)):
	job = db.get(TranscriptionJob, tid)
	if not job or not job.transcription_detail:
		raise HTTPException(404, "Transcription not found or not completed")
	if not prompt:
		prompt = job.transcription_detail.formatted_text[:500] + "..."
	try:
		job_id = f"generate_image_{tid}"
		q.enqueue_call(
			func='apps.backend.worker.generate_image_job',
			args=[tid, prompt],
			job_id=job_id,
			timeout=600
		)
		return {"message": "Image generation started", "job_id": job_id, "prompt": prompt}
	except Exception as e:
		raise HTTPException(500, f"Failed to start image generation: {str(e)}")
