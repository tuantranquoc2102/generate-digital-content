# Digital Content Creator - Audio Transcription App

Ứng dụng chuyển đổi file audio (MP3) thành text sử dụng faster-whisper, được xây dựng với FastAPI backend, Next.js frontend, và MinIO storage.

## Kiến trúc hệ thống

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Next.js   │────│   FastAPI   │────│ PostgreSQL  │
│  Frontend   │    │   Backend   │    │  Database   │
│   :3000     │    │    :8000    │    │    :5432    │
└─────────────┘    └─────────────┘    └─────────────┘
       │                  │                  │
       │                  │                  │
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   MinIO     │    │    Redis    │    │ RQ Worker   │
│  Storage    │    │   Queue     │    │(Whisper AI) │
│   :9000     │    │    :6379    │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
```

## Luồng xử lý (Workflow)

1. **Upload File**: Người dùng chọn file MP3 từ frontend
2. **Presigned URL**: Frontend yêu cầu presigned URL từ API
3. **Upload to MinIO**: File được upload qua proxy từ frontend tới MinIO
4. **Create Job**: Tạo transcription job và lưu vào database
5. **Queue Processing**: Job được đưa vào Redis queue cho worker xử lý
6. **AI Processing**: RQ Worker sử dụng faster-whisper để transcribe
7. **Save Result**: Kết quả được lưu vào database
8. **View Result**: Người dùng có thể xem kết quả trên frontend

## Cách chạy ứng dụng

### 1. Khởi động toàn bộ hệ thống
```bash
docker compose up -d
```

### 2. Kiểm tra trạng thái services
```bash
docker compose ps
```

### 3. Xem logs
```bash
# API logs
docker compose logs api

# Worker logs 
docker compose logs worker

# Frontend logs
docker compose logs web
```

## Truy cập các services

- **Frontend**: http://localhost:3000
- **API Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001 (user: minio, pass: minio123)
- **MinIO API**: http://localhost:9000

## API Endpoints

### 1. Health Check
```bash
GET /health
```

### 2. Tạo Presigned URL cho upload
```bash
POST /uploads/presign
Content-Type: application/json
{
  "file_name": "audio.mp3",
  "content_type": "audio/mpeg"
}
```

### 3. Tạo transcription job
```bash
POST /transcriptions
Content-Type: application/json
{
  "fileKey": "audios/file-key.mp3",
  "language": "auto",
  "engine": "local"
}
```

### 4. Lấy kết quả transcription
```bash
GET /transcriptions/{job_id}
```

## Cấu hình Environment Variables

File `.env`:
```bash
# Database
POSTGRES_HOST=db
POSTGRES_DB=any2text
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# MinIO/S3
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=minio
S3_SECRET_KEY=minio123
S3_BUCKET=uploads

# API
API_CORS_ORIGINS=http://localhost:3000

# Frontend
NEXT_PUBLIC_API_BASE=http://localhost:8000
```

## Cách sử dụng qua Frontend

1. Mở http://localhost:3000
2. Chọn file MP3 từ máy tính
3. Nhấn nút "Upload và Transcribe"
4. Hệ thống sẽ:
   - Upload file lên MinIO
   - Tạo background job
   - Chuyển đến trang kết quả
5. Xem kết quả transcription khi hoàn thành

## Các công nghệ sử dụng

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL
- **Queue**: Redis + RQ
- **AI**: faster-whisper (CPU-based)
- **Storage**: MinIO (S3-compatible)
- **Frontend**: Next.js, TypeScript
- **Container**: Docker Compose

## Troubleshooting

### Lỗi upload file
- Kiểm tra MinIO container đang chạy
- Kiểm tra logs của web service

### Lỗi transcription
- Kiểm tra logs của worker container
- Đảm bảo file MP3 đã được upload thành công

### Lỗi database
- Kiểm tra PostgreSQL container
- Xem logs của api container

### Rebuild và restart
```bash
# Dừng tất cả
docker compose down

# Build lại từ đầu
docker compose build --no-cache

# Khởi động lại
docker compose up -d
```

## Tính năng

✅ Upload MP3 files  
✅ Automatic transcription with faster-whisper  
✅ Background job processing  
✅ PostgreSQL database storage  
✅ MinIO file storage  
✅ Real-time job status tracking  
✅ Responsive web interface  

## Phát triển tiếp theo

- [ ] Support nhiều định dạng audio (WAV, M4A, etc.)
- [ ] Tích hợp cloud AI services (OpenAI Whisper, Google Speech-to-Text)
- [ ] Hỗ trợ batch processing nhiều files
- [ ] Thêm authentication và authorization
- [ ] Export kết quả ra file (TXT, SRT, VTT)
- [ ] Tối ưu hóa performance cho files lớn
