"use client";
import { useEffect, useState } from "react";
import { getTranscription } from "../../api-client";
import { useParams } from "next/navigation";

export default function JobPage() {
  const params = useParams<{ id: string }>();
  const id = params.id;
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    let t: any;
    async function poll() {
      try {
        const r = await getTranscription(id);
        setData(r);
        if (r.status === "done" || r.status === "error") return;
      } catch (e) { console.error(e); }
      t = setTimeout(poll, 1500);
    }
    poll();
    return () => clearTimeout(t);
  }, [id]);

  return (
    <main className="min-h-screen p-6">
      <h1 className="text-2xl font-semibold mb-4">Job: {id}</h1>
      {!data && <p>Loading...</p>}
      {data && (
        <div className="space-y-3">
          <p>Status: <b>{data.status}</b></p>
          
          {/* Display YouTube info if available */}
          {data.youtube_url && (
            <div className="bg-blue-50 p-3 rounded">
              <h3 className="font-medium text-blue-800">📺 YouTube Video</h3>
              {data.title && <p className="text-sm text-blue-600">Title: {data.title}</p>}
              <a 
                href={data.youtube_url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-blue-500 hover:underline text-sm"
              >
                {data.youtube_url}
              </a>
            </div>
          )}
          
          {/* Display file info for regular uploads */}
          {data.file_key && !data.youtube_url && (
            <div className="bg-green-50 p-3 rounded">
              <h3 className="font-medium text-green-800">🎵 Audio File</h3>
              <p className="text-sm text-green-600">File: {data.file_key}</p>
            </div>
          )}
          
          {data.error && <pre className="text-red-600">{data.error}</pre>}
          {data.result?.text && (
            <>
              <h2 className="text-xl font-bold mt-4">Transcript</h2>
              <pre className="whitespace-pre-wrap bg-gray-50 p-3 rounded">{data.result.text}</pre>
            </>
          )}
        </div>
      )}
    </main>
  );
}
