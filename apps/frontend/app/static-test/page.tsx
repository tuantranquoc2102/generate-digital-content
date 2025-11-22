export default function StaticTestPage() {
  const mockJobData = {
    id: "085c2f55-d4bd-4792-ac12-f3a60d6ffc64",
    status: "done",
    youtube_url: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    title: "Rick Astley - Never Gonna Give You Up (Official Video) (4K Remaster)",
    file_key: "youtube/085c2f55-d4bd-4792-ac12-f3a60d6ffc64.mp3"
  };

  const mockDetailData = {
    id: "192bed0c-c7d5-4948-8a18-424076eeb153",
    job_id: "085c2f55-d4bd-4792-ac12-f3a60d6ffc64",
    formatted_text: "We're no strangers to love You know the rules and so do I I've built commitments while I'm thinking of You wouldn't get this from any other guy I just wanna tell you how I'm feeling Gotta make you understand Never gonna give you up Never gonna let you down Never gonna run around and desert you Never gonna make you cry Never gonna say goodbye Never gonna tell a lie and hurt you",
    word_count: 354,
    result_json: JSON.stringify({
      text: "We're no strangers to love...",
      segments: [
        { id: 1, start: 0.0, end: 27.0, text: "We're no strangers to love You know the rules and so do I" },
        { id: 2, start: 27.0, end: 35.0, text: "I've built commitments while I'm thinking of You wouldn't get this from any other guy" }
      ]
    })
  };

  return (
    <main style={{ minHeight: "100vh", padding: "24px" }}>
      <h1 style={{ fontSize: "2rem", fontWeight: "600", marginBottom: "16px" }}>
        Job: {mockJobData.id}
      </h1>
      
      <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
        <p>Status: <strong>{mockJobData.status}</strong></p>
        
        {/* YouTube info */}
        <div style={{ 
          backgroundColor: "#dbeafe", 
          padding: "12px", 
          borderRadius: "8px" 
        }}>
          <h3 style={{ fontWeight: "500", color: "#1e40af", marginBottom: "4px" }}>
            📺 YouTube Video
          </h3>
          <p style={{ fontSize: "14px", color: "#2563eb", marginBottom: "4px" }}>
            Title: {mockJobData.title}
          </p>
          <a 
            href={mockJobData.youtube_url}
            target="_blank"
            rel="noopener noreferrer"
            style={{ fontSize: "14px", color: "#3b82f6", textDecoration: "underline" }}
          >
            {mockJobData.youtube_url}
          </a>
        </div>

        {/* Transcription content */}
        <div>
          <h2 style={{ fontSize: "1.5rem", fontWeight: "700", marginTop: "16px", marginBottom: "8px" }}>
            📝 Transcript
          </h2>
          <div style={{ 
            backgroundColor: "#f9fafb", 
            padding: "16px", 
            borderRadius: "8px" 
          }}>
            <p style={{ fontSize: "14px", color: "#6b7280", marginBottom: "8px" }}>
              Word count: {mockDetailData.word_count}
            </p>
            <pre style={{ 
              whiteSpace: "pre-wrap", 
              fontSize: "14px", 
              lineHeight: "1.6",
              margin: 0,
              fontFamily: "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace"
            }}>
              {mockDetailData.formatted_text}
            </pre>
          </div>
        </div>

        {/* Debug info */}
        <details style={{ marginTop: "16px" }}>
          <summary style={{ 
            cursor: "pointer", 
            fontWeight: "500", 
            color: "#6b7280" 
          }}>
            Debug Info
          </summary>
          <div style={{ 
            marginTop: "8px", 
            display: "grid", 
            gridTemplateColumns: "1fr 1fr", 
            gap: "16px" 
          }}>
            <div style={{ backgroundColor: "#dbeafe", padding: "12px", borderRadius: "8px" }}>
              <h4 style={{ fontWeight: "700", fontSize: "14px", marginBottom: "8px" }}>
                Job Data:
              </h4>
              <pre style={{ fontSize: "12px", overflow: "auto", margin: 0 }}>
                {JSON.stringify(mockJobData, null, 2)}
              </pre>
            </div>
            <div style={{ backgroundColor: "#dcfce7", padding: "12px", borderRadius: "8px" }}>
              <h4 style={{ fontWeight: "700", fontSize: "14px", marginBottom: "8px" }}>
                Detail Data:
              </h4>
              <pre style={{ fontSize: "12px", overflow: "auto", margin: 0 }}>
                {JSON.stringify(mockDetailData, null, 2)}
              </pre>
            </div>
          </div>
        </details>
      </div>
    </main>
  );
}