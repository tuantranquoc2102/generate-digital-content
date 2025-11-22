"use client";
import { useEffect, useState } from "react";

export default function TestAPIPage() {
  const [jobData, setJobData] = useState(null);
  const [detailData, setDetailData] = useState(null);
  const [errors, setErrors] = useState<string[]>([]);

  useEffect(() => {
    const testAPI = async () => {
      const jobId = "085c2f55-d4bd-4792-ac12-f3a60d6ffc64";
      
      // Test job endpoint
      try {
        console.log("Testing job endpoint...");
        const jobResponse = await fetch(`http://localhost:8000/transcriptions/${jobId}`);
        console.log("Job response status:", jobResponse.status);
        if (jobResponse.ok) {
          const job = await jobResponse.json();
          console.log("Job data:", job);
          setJobData(job);
        } else {
          setErrors(prev => [...prev, `Job endpoint failed: ${jobResponse.status}`]);
        }
      } catch (e) {
        console.error("Job endpoint error:", e);
        setErrors(prev => [...prev, `Job endpoint error: ${e}`]);
      }

      // Test detail endpoint  
      try {
        console.log("Testing detail endpoint...");
        const detailResponse = await fetch(`http://localhost:8000/transcriptions/${jobId}/detail`);
        console.log("Detail response status:", detailResponse.status);
        if (detailResponse.ok) {
          const detail = await detailResponse.json();
          console.log("Detail data:", detail);
          setDetailData(detail);
        } else {
          setErrors(prev => [...prev, `Detail endpoint failed: ${detailResponse.status}`]);
        }
      } catch (e) {
        console.error("Detail endpoint error:", e);
        setErrors(prev => [...prev, `Detail endpoint error: ${e}`]);
      }
    };

    testAPI();
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">API Test Page</h1>
      
      {errors.length > 0 && (
        <div className="bg-red-50 p-4 rounded mb-4">
          <h3 className="font-bold text-red-800">Errors:</h3>
          {errors.map((error, i) => (
            <p key={i} className="text-red-600 text-sm">{error}</p>
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-blue-50 p-4 rounded">
          <h3 className="font-bold mb-2">Job Data:</h3>
          <pre className="text-xs overflow-auto">{JSON.stringify(jobData, null, 2)}</pre>
        </div>

        <div className="bg-green-50 p-4 rounded">
          <h3 className="font-bold mb-2">Detail Data:</h3>
          <pre className="text-xs overflow-auto">{JSON.stringify(detailData, null, 2)}</pre>
        </div>
      </div>

      {detailData?.formatted_text && (
        <div className="mt-4 bg-gray-50 p-4 rounded">
          <h3 className="font-bold mb-2">Formatted Text:</h3>
          <p className="text-sm">{detailData.formatted_text}</p>
        </div>
      )}
    </div>
  );
}