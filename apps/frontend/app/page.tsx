"use client";

import { useState } from "react";
import { presign, createTranscription } from "./api-client";
import { useRouter } from "next/navigation";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [progress, setProgress] = useState<number>(0);
  const [busy, setBusy] = useState(false);
  const router = useRouter();

  async function handleUpload() {
    if (!file) return;
    setBusy(true);
    try {
      const contentType = file.type || "application/octet-stream";

      // 1) presign
      const { upload_url, file_key } = await presign(file.name, contentType);
      console.log("Got presigned URL:", upload_url);
      
      // 2) Upload via Next.js proxy to MinIO
      console.log('Uploading file via proxy with URL:', upload_url);
      const putResp = await fetch(`/api/minio-proxy`, {
        method: "PUT",
        headers: { 
          "Content-Type": contentType,
          "x-minio-url": upload_url
        },
        body: file,
      });

      console.log('Upload response status:', putResp.status);
      if (!putResp.ok) {
        const errorText = await putResp.text().catch(() => "Unknown error");
        console.error("Upload error response:", errorText);
        throw new Error(`Upload failed ${putResp.status}: ${errorText}`);
      }
      console.log('File uploaded successfully');

      // 3) tạo job
      const job = await createTranscription({ fileKey: file_key, language: "auto", engine: "local" });
      router.push(`/transcriptions/${job.id}`);
    } catch (err: any) {
      console.error("Upload failed:", err);
      alert(`Upload failed: ${err?.message || err}`);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="min-h-screen flex flex-col items-center justify-center gap-6 p-6">
      <h1 className="text-3xl font-bold">any2text — MP3 to Text (Skeleton)</h1>
      <div className="w-full max-w-xl border rounded-lg p-6">
        <input
          type="file"
          accept="audio/*,video/*"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className="mb-4"
        />
        <button
          disabled={!file || busy}
          onClick={handleUpload}
          className="px-4 py-2 rounded bg-black text-white disabled:opacity-50"
        >
          {busy ? "Uploading..." : "Upload & Transcribe"}
        </button>
        {progress > 0 && (
          <div className="mt-4">
            <div className="w-full bg-gray-200 h-2 rounded">
              <div className="bg-black h-2 rounded" style={{ width: `${progress}%` }}></div>
            </div>
            <p className="text-sm mt-2">{progress}%</p>
          </div>
        )}
      </div>
      
      <div className="flex gap-4 text-sm">
        <span className="px-4 py-2 bg-gray-100 rounded">
          🎵 Upload MP3
        </span>
        <span className="text-gray-500">hoặc</span>
        <a 
          href="/youtube"
          className="px-4 py-2 border rounded hover:bg-gray-50"
        >
          📺 YouTube Transcription →
        </a>
      </div>
      
      <p className="text-sm text-gray-500">MinIO console: http://localhost:9001 (user: minio / pass: minio123)</p>
    </main>
  );
}
