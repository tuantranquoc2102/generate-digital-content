"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

export default function JobPage() {
  const params = useParams<{ id: string }>();
  const id = params.id;
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    let t: any;
    async function poll() {
      try {
        const response = await fetch(`http://localhost:8000/transcriptions/${id}`, { 
          cache: "no-store" 
        });
        if (response.ok) {
          const result = await response.json();
          console.log("API Response:", result);
          setData(result);
        }
        
        // Stop polling if done or error
        if (data?.status === "done" || data?.status === "error") return;
      } catch (e) { 
        console.error("API Error:", e); 
      }
      t = setTimeout(poll, 1500);
    }
    poll();
    return () => clearTimeout(t);
  }, [id, data?.status]);

  return (
    <div style={{ padding: "24px", maxWidth: "1200px", margin: "0 auto" }}>
      <h1 style={{ fontSize: "2rem", fontWeight: "600", marginBottom: "16px" }}>
        Job: {id}
      </h1>
      
      {!data && <p>Loading...</p>}
      
      {data && (
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          <p>Status: <strong>{data.status}</strong></p>
          
          {/* YouTube info */}
          {data.youtube_url && (
            <div style={{ 
              backgroundColor: "#dbeafe", 
              padding: "16px", 
              borderRadius: "8px" 
            }}>
              <h3 style={{ fontWeight: "600", color: "#1e40af", margin: "0 0 8px 0" }}>
                📺 YouTube Video
              </h3>
              {data.title && (
                <p style={{ fontSize: "14px", color: "#2563eb", margin: "0 0 8px 0" }}>
                  Title: {data.title}
                </p>
              )}
              <a 
                href={data.youtube_url}
                target="_blank"
                rel="noopener noreferrer"
                style={{ fontSize: "14px", color: "#3b82f6", textDecoration: "underline" }}
              >
                {data.youtube_url}
              </a>
            </div>
          )}

          {/* Error display */}
          {data.error && (
            <div style={{ 
              backgroundColor: "#fef2f2", 
              color: "#dc2626", 
              padding: "16px", 
              borderRadius: "8px" 
            }}>
              <pre>{data.error}</pre>
            </div>
          )}

          {/* Transcription content */}
          {data.result?.text && (
            <div>
              <h2 style={{ fontSize: "1.5rem", fontWeight: "700", margin: "24px 0 16px 0" }}>
                📝 Transcript
              </h2>
              <div style={{ 
                backgroundColor: "#f9fafb", 
                padding: "20px", 
                borderRadius: "8px",
                border: "1px solid #e5e7eb"
              }}>
                <div style={{ 
                  whiteSpace: "pre-wrap", 
                  fontSize: "14px", 
                  lineHeight: "1.6",
                  fontFamily: "ui-sans-serif, system-ui, sans-serif"
                }}>
                  {data.result.text}
                </div>
              </div>
            </div>
          )}

          {/* Segments display */}
          {data.result?.segments && (
            <details style={{ marginTop: "16px" }}>
              <summary style={{ 
                cursor: "pointer", 
                fontWeight: "600", 
                color: "#374151",
                padding: "8px",
                backgroundColor: "#f3f4f6",
                borderRadius: "4px"
              }}>
                🔍 View Detailed Segments ({data.result.segments.length} segments)
              </summary>
              <div style={{ 
                marginTop: "8px", 
                backgroundColor: "#f0f9ff", 
                padding: "16px", 
                borderRadius: "8px",
                maxHeight: "400px",
                overflowY: "auto"
              }}>
                {data.result.segments.map((segment: any, i: number) => (
                  <div key={i} style={{ 
                    marginBottom: "12px", 
                    paddingBottom: "12px", 
                    borderBottom: i < data.result.segments.length - 1 ? "1px solid #e0f2fe" : "none" 
                  }}>
                    <div style={{ 
                      fontSize: "12px", 
                      color: "#0369a1", 
                      fontWeight: "500",
                      marginBottom: "4px"
                    }}>
                      {segment.start?.toFixed(1)}s - {segment.end?.toFixed(1)}s
                    </div>
                    <div style={{ fontSize: "14px", color: "#1f2937" }}>
                      {segment.text}
                    </div>
                  </div>
                ))}
              </div>
            </details>
          )}

          {/* Debug section */}
          <details style={{ marginTop: "24px" }}>
            <summary style={{ 
              cursor: "pointer", 
              fontSize: "14px", 
              color: "#6b7280",
              fontWeight: "500"
            }}>
              Debug: Raw API Response
            </summary>
            <pre style={{ 
              marginTop: "8px", 
              backgroundColor: "#1f2937", 
              color: "#f9fafb",
              padding: "16px", 
              borderRadius: "8px",
              fontSize: "12px",
              overflow: "auto"
            }}>
              {JSON.stringify(data, null, 2)}
            </pre>
          </details>
        </div>
      )}
    </div>
  );
}
