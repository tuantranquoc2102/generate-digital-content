"use client";

import { useState } from "react";
import { presign, createTranscription } from "../api-client";
import { useRouter } from "next/navigation";

export default function LegacyUpload() {
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
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-6 text-center">Legacy Audio Upload</h1>
        <p className="text-gray-600 mb-8 text-center">
          Upload audio or video files directly for transcription
        </p>

        <div className="bg-white border border-gray-200 rounded-lg p-8 shadow-sm">
          <input
            type="file"
            accept="audio/*,video/*"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className="w-full mb-6 p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          
          <button
            disabled={!file || busy}
            onClick={handleUpload}
            className="w-full px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
          >
            {busy ? "Uploading..." : "Upload & Transcribe"}
          </button>
          
          {progress > 0 && (
            <div className="mt-6">
              <div className="w-full bg-gray-200 h-2 rounded-full">
                <div 
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                  style={{ width: `${progress}%` }}
                ></div>
              </div>
              <p className="text-sm mt-2 text-gray-600 text-center">{progress}%</p>
            </div>
          )}
        </div>

        <div className="mt-8 text-center">
          <p className="text-sm text-gray-500 mb-4">
            Prefer YouTube? Try our YouTube transcription feature for better results
          </p>
          <a 
            href="/youtube"
            className="inline-block px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors font-medium"
          >
            📺 YouTube Transcription
          </a>
        </div>
      </div>
    </div>
  );
}