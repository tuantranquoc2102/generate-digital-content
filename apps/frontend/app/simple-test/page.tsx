export default function SimpleTestPage() {
  const jobId = "085c2f55-d4bd-4792-ac12-f3a60d6ffc64";
  
  const testAPI = async () => {
    try {
      const response = await fetch(`http://localhost:8000/transcriptions/${jobId}/detail`);
      const data = await response.json();
      alert(`Success! Formatted text length: ${data.formatted_text?.length || 'N/A'}`);
    } catch (e) {
      alert(`Error: ${e}`);
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <h1>Simple API Test</h1>
      <button onClick={testAPI} style={{ 
        padding: "10px 20px", 
        backgroundColor: "#007cba", 
        color: "white", 
        border: "none", 
        borderRadius: "4px",
        cursor: "pointer"
      }}>
        Test API Call
      </button>
      
      <div style={{ marginTop: "20px" }}>
        <h3>Manual Test:</h3>
        <p>Open browser console and run:</p>
        <code style={{ 
          display: "block", 
          backgroundColor: "#f5f5f5", 
          padding: "10px", 
          marginTop: "10px"
        }}>
          {`fetch('http://localhost:8000/transcriptions/${jobId}/detail').then(r => r.json()).then(console.log)`}
        </code>
      </div>
    </div>
  );
}