export const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export async function presign(file_name: string, content_type: string) {
  const r = await fetch(`${API_BASE}/uploads/presign`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({file_name, content_type }),
  });
  if (!r.ok) throw new Error("presign failed");
  return r.json() as Promise<{ upload_url: string; file_key: string }>;
}

export async function createTranscription(body: { fileKey: string; language?: string; engine?: string }) {
  const r = await fetch(`${API_BASE}/transcriptions`, {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body)
  });
  if (!r.ok) throw new Error("create job failed");
  return r.json() as Promise<{ id: string; status: string }>;
}

export async function getTranscription(id: string) {
  const r = await fetch(`/api/transcriptions/${id}/detail`, { cache: "no-store" });
  if (!r.ok) throw new Error("get transcription detail failed");
  return r.json() as Promise<{
    id: string;
    job_id: string;
    result_json?: string;
    formatted_text?: string;
    summary?: string;
    keywords?: string;
    word_count?: number;
    confidence_score?: number;
  }>;
}

export async function getTranscriptionJob(id: string) {
  const r = await fetch(`/api/transcriptions/${id}`, { cache: "no-store" });
  if (!r.ok) throw new Error("get transcription job failed");
  return r.json() as Promise<{
    id: string;
    status: string;
    error?: string;
    file_url?: string;
    file_key?: string;
    youtube_url?: string;
    title?: string;
    engine?: string;
    language?: string;
    duration?: number;
  }>;
}

export async function createYouTubeTranscription(body: { youtube_url: string; language?: string; engine?: string }) {
  const r = await fetch(`${API_BASE}/youtube/transcriptions`, {
    method: "POST", 
    headers: { "Content-Type": "application/json" }, 
    body: JSON.stringify(body)
  });
  if (!r.ok) throw new Error("create YouTube job failed");
  return r.json() as Promise<{ id: string; status: string; youtube_url: string }>;
}

// Helper function để tạo direct download URL cho MP3 file từ MinIO
export function getFileDownloadUrl(file_key: string): string {
  const MINIO_BASE = "http://localhost:9000"; // MinIO endpoint
  const BUCKET = "uploads"; // S3 bucket name
  return `${MINIO_BASE}/${BUCKET}/${file_key}`;
}
