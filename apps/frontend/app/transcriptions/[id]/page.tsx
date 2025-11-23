"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

export default function JobPage() {
  const params = useParams<{ id: string }>();
  const id = params.id;
  const [data, setData] = useState<any>(null);
  const [imageFiles, setImageFiles] = useState<FileList | null>(null);
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState<{dialogue: boolean, image: boolean}>({dialogue: false, image: false});
  const [customPrompt, setCustomPrompt] = useState("");

  useEffect(() => {
    let t: any;
    async function poll() {
      try {
        const response = await fetch(`http://localhost:8000/transcriptions/${id}/full`, { 
          cache: "no-store" 
        });
        if (response.ok) {
          const result = await response.json();
          console.log("API Response:", result);
          setData(result);
        }
        
        // Stop polling if done or error
        if (data?.job?.status === "done" || data?.job?.status === "error") return;
      } catch (e) { 
        console.error("API Error:", e); 
      }
      t = setTimeout(poll, 1500);
    }
    poll();
    return () => clearTimeout(t);
  }, [id, data?.job?.status]);

  const handleImageUpload = async () => {
    if (!imageFiles || imageFiles.length === 0) return;
    
    setUploading(true);
    try {
      for (const file of Array.from(imageFiles)) {
        // First, presign upload
        const presignResponse = await fetch("http://localhost:8000/uploads/presign", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            file_name: file.name,
            content_type: file.type
          })
        });
        
        if (!presignResponse.ok) throw new Error("Presign failed");
        
        const { upload_url, file_key } = await presignResponse.json();
        
        // Upload file to S3/MinIO
        const uploadResponse = await fetch(upload_url, {
          method: "PUT",
          body: file,
          headers: { "Content-Type": file.type }
        });
        
        if (!uploadResponse.ok) throw new Error("Upload failed");
        
        // Register image with transcription
        const registerResponse = await fetch(`http://localhost:8000/transcriptions/${id}/images`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            image_type: "uploaded",
            file_key: file_key,
            file_url: upload_url.split('?')[0], // Remove query params
            filename: file.name,
            mime_type: file.type,
            description: `User uploaded image: ${file.name}`
          })
        });
        
        if (!registerResponse.ok) throw new Error("Registration failed");
      }
      
      // Refresh data
      window.location.reload();
    } catch (e) {
      alert(`Upload failed: ${e}`);
    } finally {
      setUploading(false);
    }
  };

  const handleFormatDialogue = async () => {
    setProcessing(prev => ({...prev, dialogue: true}));
    try {
      const response = await fetch(`http://localhost:8000/transcriptions/${id}/format-dialogue`, {
        method: "POST"
      });
      
      if (!response.ok) throw new Error("Failed to start dialogue formatting");
      
      const result = await response.json();
      alert(`Dialogue formatting started! Job ID: ${result.job_id}`);
      
      // Refresh data after a delay
      setTimeout(() => window.location.reload(), 3000);
    } catch (e) {
      alert(`Dialogue formatting failed: ${e}`);
    } finally {
      setProcessing(prev => ({...prev, dialogue: false}));
    }
  };

  const handleGenerateImage = async () => {
    setProcessing(prev => ({...prev, image: true}));
    try {
      const response = await fetch(`http://localhost:8000/transcriptions/${id}/generate-image`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: customPrompt || undefined
        })
      });
      
      if (!response.ok) throw new Error("Failed to start image generation");
      
      const result = await response.json();
      alert(`Image generation started! Job ID: ${result.job_id}\\nPrompt: ${result.prompt}`);
      
      // Refresh data after a delay
      setTimeout(() => window.location.reload(), 5000);
    } catch (e) {
      alert(`Image generation failed: ${e}`);
    } finally {
      setProcessing(prev => ({...prev, image: false}));
    }
  };

  return (
    <div style={{ padding: "24px", maxWidth: "1200px", margin: "0 auto" }}>
      <h1 style={{ fontSize: "2rem", fontWeight: "600", marginBottom: "16px" }}>
        Job: {id}
      </h1>
      
      {!data && <p>Loading...</p>}
      
      {data && (
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          <p>Status: <strong>{data.job?.status}</strong></p>
          
          {/* YouTube info */}
          {data.job?.youtube_url && (
            <div style={{ 
              backgroundColor: "#dbeafe", 
              padding: "16px", 
              borderRadius: "8px" 
            }}>
              <h3 style={{ fontWeight: "600", color: "#1e40af", margin: "0 0 8px 0" }}>
                📺 YouTube Video
              </h3>
              {data.job?.title && (
                <p style={{ fontSize: "14px", color: "#2563eb", margin: "0 0 8px 0" }}>
                  Title: {data.job.title}
                </p>
              )}
              <a 
                href={data.job.youtube_url}
                target="_blank"
                rel="noopener noreferrer"
                style={{ fontSize: "14px", color: "#3b82f6", textDecoration: "underline" }}
              >
                {data.job.youtube_url}
              </a>
            </div>
          )}

          {/* Error display */}
          {data.job?.error && (
            <div style={{ 
              backgroundColor: "#fef2f2", 
              color: "#dc2626", 
              padding: "16px", 
              borderRadius: "8px" 
            }}>
              <pre>{data.job.error}</pre>
            </div>
          )}

          {/* Original Transcription content */}
          {data.job?.result?.text && (
            <div>
              <h2 style={{ fontSize: "1.5rem", fontWeight: "700", margin: "24px 0 16px 0" }}>
                📝 Original Transcript
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
                  {data.job.result.text}
                </div>
              </div>
            </div>
          )}

          {/* Formatted Dialogue */}
          {data.detail?.summary && data.detail.keywords === "formatted_dialogue" && (
            <div>
              <h2 style={{ fontSize: "1.5rem", fontWeight: "700", margin: "24px 0 16px 0" }}>
                💬 Formatted Dialogue
              </h2>
              <div style={{ 
                backgroundColor: "#f0f9ff", 
                padding: "20px", 
                borderRadius: "8px",
                border: "1px solid #bfdbfe"
              }}>
                <div style={{ 
                  whiteSpace: "pre-wrap", 
                  fontSize: "14px", 
                  lineHeight: "1.6",
                  fontFamily: "ui-sans-serif, system-ui, sans-serif"
                }}>
                  {data.detail.summary}
                </div>
              </div>
            </div>
          )}

          {/* AI Processing Actions */}
          {data.job?.status === "done" && data.job?.result?.text && (
            <div style={{
              backgroundColor: "#f8fafc",
              padding: "20px",
              borderRadius: "8px",
              border: "1px solid #e2e8f0"
            }}>
              <h3 style={{ fontSize: "1.25rem", fontWeight: "600", margin: "0 0 16px 0" }}>
                🤖 AI Processing
              </h3>
              
              <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                {/* Format Dialogue Button */}
                <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                  <button
                    onClick={handleFormatDialogue}
                    disabled={processing.dialogue}
                    style={{
                      padding: "10px 16px",
                      backgroundColor: processing.dialogue ? "#9ca3af" : "#3b82f6",
                      color: "white",
                      border: "none",
                      borderRadius: "6px",
                      cursor: processing.dialogue ? "not-allowed" : "pointer",
                      fontSize: "14px",
                      fontWeight: "500"
                    }}
                  >
                    {processing.dialogue ? "Processing..." : "💬 Format as Dialogue (OpenAI)"}
                  </button>
                  <span style={{ fontSize: "12px", color: "#6b7280" }}>
                    Convert transcript to Speaker1: text; Speaker2: text format
                  </span>
                </div>

                {/* Generate Image Section */}
                <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                    <button
                      onClick={handleGenerateImage}
                      disabled={processing.image}
                      style={{
                        padding: "10px 16px",
                        backgroundColor: processing.image ? "#9ca3af" : "#10b981",
                        color: "white",
                        border: "none",
                        borderRadius: "6px",
                        cursor: processing.image ? "not-allowed" : "pointer",
                        fontSize: "14px",
                        fontWeight: "500"
                      }}
                    >
                      {processing.image ? "Generating..." : "🎨 Generate Scene Image (DALL-E)"}
                    </button>
                  </div>
                  <input
                    type="text"
                    placeholder="Custom prompt (optional) - leave empty for AI-generated prompt"
                    value={customPrompt}
                    onChange={(e) => setCustomPrompt(e.target.value)}
                    style={{
                      padding: "8px 12px",
                      border: "1px solid #d1d5db",
                      borderRadius: "6px",
                      fontSize: "14px",
                      width: "100%",
                      boxSizing: "border-box"
                    }}
                  />
                </div>
              </div>
            </div>
          )}

          {/* Image Upload Section */}
          {data.job?.status === "done" && (
            <div style={{
              backgroundColor: "#fef7f0",
              padding: "20px",
              borderRadius: "8px",
              border: "1px solid #fed7aa"
            }}>
              <h3 style={{ fontSize: "1.25rem", fontWeight: "600", margin: "0 0 16px 0" }}>
                🖼️ Upload Related Images
              </h3>
              
              <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                <input
                  type="file"
                  multiple
                  accept="image/*"
                  onChange={(e) => setImageFiles(e.target.files)}
                  style={{
                    padding: "8px",
                    border: "1px solid #d1d5db",
                    borderRadius: "6px",
                    fontSize: "14px"
                  }}
                />
                <button
                  onClick={handleImageUpload}
                  disabled={!imageFiles || uploading}
                  style={{
                    padding: "10px 16px",
                    backgroundColor: (!imageFiles || uploading) ? "#9ca3af" : "#f59e0b",
                    color: "white",
                    border: "none",
                    borderRadius: "6px",
                    cursor: (!imageFiles || uploading) ? "not-allowed" : "pointer",
                    fontSize: "14px",
                    fontWeight: "500",
                    alignSelf: "flex-start"
                  }}
                >
                  {uploading ? "Uploading..." : "📤 Upload Images"}
                </button>
              </div>
            </div>
          )}

          {/* Display Uploaded/Generated Images */}
          {data.images && data.images.length > 0 && (
            <div>
              <h2 style={{ fontSize: "1.5rem", fontWeight: "700", margin: "24px 0 16px 0" }}>
                🖼️ Related Images
              </h2>
              <div style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fill, minmax(250px, 1fr))",
                gap: "16px"
              }}>
                {data.images.map((image: any, index: number) => (
                  <div key={index} style={{
                    border: "1px solid #e5e7eb",
                    borderRadius: "8px",
                    overflow: "hidden",
                    backgroundColor: "white"
                  }}>
                    <img
                      src={image.file_url}
                      alt={image.description || image.filename}
                      style={{
                        width: "100%",
                        height: "200px",
                        objectFit: "cover"
                      }}
                    />
                    <div style={{ padding: "12px" }}>
                      <div style={{
                        fontSize: "12px",
                        color: "#6b7280",
                        marginBottom: "4px",
                        fontWeight: "500"
                      }}>
                        {image.image_type} • {image.filename}
                      </div>
                      {image.description && (
                        <div style={{
                          fontSize: "12px",
                          color: "#374151",
                          lineHeight: "1.4"
                        }}>
                          {image.description}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Segments display */}
          {data.job?.result?.segments && (
            <details style={{ marginTop: "16px" }}>
              <summary style={{ 
                cursor: "pointer", 
                fontWeight: "600", 
                color: "#374151",
                padding: "8px",
                backgroundColor: "#f3f4f6",
                borderRadius: "4px"
              }}>
                🔍 View Detailed Segments ({data.job.result.segments.length} segments)
              </summary>
              <div style={{ 
                marginTop: "8px", 
                backgroundColor: "#f0f9ff", 
                padding: "16px", 
                borderRadius: "8px",
                maxHeight: "400px",
                overflowY: "auto"
              }}>
                {data.job.result.segments.map((segment: any, i: number) => (
                  <div key={i} style={{ 
                    marginBottom: "12px", 
                    paddingBottom: "12px", 
                    borderBottom: i < data.job.result.segments.length - 1 ? "1px solid #e0f2fe" : "none" 
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
