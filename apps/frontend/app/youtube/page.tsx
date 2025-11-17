"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { createYouTubeTranscription } from "../api-client";

export default function YouTubePage() {
  const [youtubeUrl, setYoutubeUrl] = useState("");
  const [busy, setBusy] = useState(false);
  const router = useRouter();

  async function handleYouTubeTranscription() {
    if (!youtubeUrl.trim()) {
      alert("Vui lòng nhập URL YouTube");
      return;
    }

    // Validate YouTube URL
    if (!youtubeUrl.includes("youtube.com") && !youtubeUrl.includes("youtu.be")) {
      alert("URL không hợp lệ. Vui lòng nhập URL YouTube hợp lệ");
      return;
    }

    setBusy(true);
    try {
      console.log("Processing YouTube URL:", youtubeUrl);
      
      // Tạo YouTube transcription job
      const job = await createYouTubeTranscription({ 
        youtube_url: youtubeUrl, 
        language: "auto", 
        engine: "local" 
      });
      
      console.log("Created YouTube job:", job.id);
      router.push(`/transcriptions/${job.id}`);
    } catch (err: any) {
      console.error("YouTube transcription failed:", err);
      alert(`Lỗi: ${err?.message || err}`);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="min-h-screen flex flex-col items-center justify-center gap-6 p-6">
      <h1 className="text-3xl font-bold">YouTube to Text Transcription</h1>
      
      <div className="w-full max-w-2xl border rounded-lg p-6">
        <div className="space-y-4">
          <div>
            <label htmlFor="youtube-url" className="block text-sm font-medium mb-2">
              YouTube URL
            </label>
            <input
              id="youtube-url"
              type="url"
              value={youtubeUrl}
              onChange={(e) => setYoutubeUrl(e.target.value)}
              placeholder="https://www.youtube.com/watch?v=..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <button
            disabled={!youtubeUrl.trim() || busy}
            onClick={handleYouTubeTranscription}
            className="w-full px-4 py-2 rounded bg-red-600 text-white disabled:opacity-50 hover:bg-red-700 transition-colors"
          >
            {busy ? "Đang xử lý..." : "Tải Audio và Transcribe"}
          </button>
          
          <div className="text-sm text-gray-600">
            <p><strong>Hỗ trợ:</strong></p>
            <ul className="list-disc list-inside space-y-1 mt-1">
              <li>YouTube videos và YouTube Shorts</li>
              <li>Tự động tải audio chất lượng cao</li>
              <li>Transcription với faster-whisper AI</li>
              <li>Lưu trữ kết quả trong database</li>
            </ul>
          </div>
        </div>
      </div>
      
      <div className="flex gap-4 text-sm">
        <a 
          href="/"
          className="px-4 py-2 border rounded hover:bg-gray-50"
        >
          ← Upload File MP3
        </a>
        <span className="text-gray-500">hoặc</span>
        <span className="px-4 py-2 bg-gray-100 rounded">
          📺 YouTube Transcription
        </span>
      </div>
      
      <p className="text-sm text-gray-500">
        MinIO console: http://localhost:9001 (user: minio / pass: minio123)
      </p>
    </main>
  );
}