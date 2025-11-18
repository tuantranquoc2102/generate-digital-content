"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { createYouTubeTranscription } from "../api-client";

export default function YouTubePage() {
  const [youtubeUrl, setYoutubeUrl] = useState("");
  const [selectedLanguage, setSelectedLanguage] = useState("auto");
  const [busy, setBusy] = useState(false);
  const router = useRouter();

  // Language options
  const languageOptions = [
    { value: "auto", label: "🌍 Tự động phát hiện" },
    { value: "vi", label: "🇻🇳 Tiếng Việt" },
    { value: "en", label: "🇺🇸 English" },
    { value: "zh", label: "🇨🇳 中文 (Chinese)" },
    { value: "ja", label: "🇯🇵 日本語 (Japanese)" },
    { value: "ko", label: "🇰🇷 한국어 (Korean)" },
    { value: "es", label: "🇪🇸 Español" },
    { value: "fr", label: "🇫🇷 Français" },
    { value: "de", label: "🇩🇪 Deutsch" },
  ];

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
      console.log("Selected language:", selectedLanguage);
      
      // Tạo YouTube transcription job
      const job = await createYouTubeTranscription({ 
        youtube_url: youtubeUrl, 
        language: selectedLanguage, 
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
          
          <div>
            <label htmlFor="language-select" className="block text-sm font-medium mb-2">
              Ngôn ngữ Transcription
            </label>
            <select
              id="language-select"
              value={selectedLanguage}
              onChange={(e) => setSelectedLanguage(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {languageOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
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
              <li>Hỗ trợ đa ngôn ngữ (Việt, Anh, Trung, Nhật...)</li>
              <li>Lưu trữ kết quả trong database</li>
            </ul>
            <div className="mt-3 space-y-2">
              <div className="p-2 bg-green-50 rounded border-l-4 border-green-400">
                <p className="text-sm font-medium">🇺🇸 Demo URLs (Reliable):</p>
                <div className="flex flex-col gap-1 mt-1">
                  <button 
                    onClick={() => setYoutubeUrl("https://www.youtube.com/watch?v=dQw4w9WgXcQ")}
                    className="text-blue-600 hover:underline text-xs text-left"
                  >
                    • Rick Astley - Never Gonna Give You Up
                  </button>
                  <button 
                    onClick={() => setYoutubeUrl("https://www.youtube.com/watch?v=jNQXAC9IVRw")}
                    className="text-blue-600 hover:underline text-xs text-left"
                  >
                    • Me at the zoo (First YouTube video)
                  </button>
                </div>
              </div>
              
              <div className="p-2 bg-blue-50 rounded border-l-4 border-blue-400">
                <p className="text-sm font-medium">🎓 Educational Content:</p>
                <div className="flex flex-col gap-1 mt-1">
                  <button 
                    onClick={() => setYoutubeUrl("https://www.youtube.com/watch?v=AuX7nPBqDts")}
                    className="text-blue-600 hover:underline text-xs text-left"
                  >
                    • TED Talk (Short & Clear Speech)
                  </button>
                  <button 
                    onClick={() => setYoutubeUrl("https://www.youtube.com/watch?v=Ks-_Mh1QhMc")}
                    className="text-blue-600 hover:underline text-xs text-left"
                  >
                    • Creative Commons Music
                  </button>
                </div>
              </div>
              
              <div className="p-2 bg-yellow-50 rounded border-l-4 border-yellow-400">
                <p className="text-sm font-medium">🇻🇳 Tiếng Việt (Tested & Working):</p>
                <div className="flex flex-col gap-1 mt-1">
                  <button 
                    onClick={() => setYoutubeUrl("https://www.youtube.com/shorts/1TicDjfLzHg")}
                    className="text-blue-600 hover:underline text-xs text-left"
                  >
                    • Working Vietnamese Short (Verified ✓)
                  </button>
                  <button 
                    onClick={() => setYoutubeUrl("https://www.youtube.com/shorts/OQSRzXMNPRo")}
                    className="text-blue-600 hover:underline text-xs text-left"
                  >
                    • Original Demo URL →
                  </button>
                </div>
              </div>
              
              <div className="p-2 bg-red-50 rounded border-l-4 border-red-400">
                <p className="text-xs text-red-600">
                  <strong>⚠️ Lưu ý:</strong> Một số video có thể bị YouTube chặn download do bản quyền hoặc giới hạn vùng miền.
                </p>
              </div>
            </div>
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