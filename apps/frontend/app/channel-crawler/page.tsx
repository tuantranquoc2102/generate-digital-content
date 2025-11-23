"use client";

"use client";
import { useState, useEffect } from "react";
import { useRouter } from 'next/navigation';
import Link from 'next/link';

interface ChannelJob {
  job_id: string;
  video_url: string;
  title: string;
  status: string;
}

interface ChannelCrawlerResult {
  channel_crawler_id: string;
  status: string;
  channel_url: string;
  total_videos_found: number;
  total_jobs_created: number;
  jobs: ChannelJob[];
  error?: string;
}

const statusColors = {
  queued: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  processing: 'bg-blue-100 text-blue-800 border-blue-200',
  done: 'bg-green-100 text-green-800 border-green-200',
  error: 'bg-red-100 text-red-800 border-red-200'
};

const statusIcons = {
  queued: '⏳',
  processing: '⚡',
  done: '✅',
  error: '❌'
};

export default function ChannelCrawler() {
  const [channelUrl, setChannelUrl] = useState('');
  const [language, setLanguage] = useState('auto');
  const [maxVideos, setMaxVideos] = useState(20);
  const [videoType, setVideoType] = useState('shorts');
  const [busy, setBusy] = useState(false);
  const [crawlerId, setCrawlerId] = useState<string | null>(null);
  const [crawlerResult, setCrawlerResult] = useState<ChannelCrawlerResult | null>(null);
  const router = useRouter();

  const languageOptions = [
    { value: 'auto', label: '🌐 Auto-detect' },
    { value: 'vi', label: '🇻🇳 Vietnamese' },
    { value: 'en', label: '🇺🇸 English' },
    { value: 'zh', label: '🇨🇳 Chinese' },
    { value: 'ja', label: '🇯🇵 Japanese' }
  ];

  const videoTypeOptions = [
    { value: 'shorts', label: '🎬 YouTube Shorts only' },
    { value: 'videos', label: '📹 Regular videos only' },
    { value: 'all', label: '🎥 All videos' }
  ];

  const handleStartCrawling = async () => {
    if (!channelUrl.trim()) {
      alert('Please enter a YouTube channel URL');
      return;
    }

    setBusy(true);
    try {
      const response = await fetch('/api/channel/crawler', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          channel_url: channelUrl,
          language: language,
          engine: 'local',
          max_videos: maxVideos,
          video_type: videoType
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data: ChannelCrawlerResult = await response.json();
      setCrawlerId(data.channel_crawler_id);
      setCrawlerResult(data);
      
      // Start polling for updates
      pollCrawlerStatus(data.channel_crawler_id);
      
    } catch (error: any) {
      console.error('Channel crawling failed:', error);
      alert(`Failed to start crawling: ${error.message}`);
    } finally {
      setBusy(false);
    }
  };

  const pollCrawlerStatus = async (id: string) => {
    try {
      const response = await fetch(`/api/channel/crawler/${id}`);
      if (response.ok) {
        const data: ChannelCrawlerResult = await response.json();
        setCrawlerResult(data);
        
        // Continue polling if still processing
        if (data.status === 'processing' || data.status === 'queued') {
          setTimeout(() => pollCrawlerStatus(id), 3000); // Poll every 3 seconds
        }
      }
    } catch (error) {
      console.error('Error polling crawler status:', error);
    }
  };

  const resetForm = () => {
    setChannelUrl('');
    setCrawlerId(null);
    setCrawlerResult(null);
  };

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">YouTube Channel Crawler</h1>
          <p className="text-gray-600">Automatically transcribe all videos from a YouTube channel</p>
        </div>

        {!crawlerId ? (
          // Input form
          <div className="bg-white border border-gray-200 rounded-lg p-8 shadow-sm">
            <div className="space-y-6">
              <div>
                <label htmlFor="channel-url" className="block text-sm font-medium mb-2">
                  YouTube Channel URL *
                </label>
                <input
                  id="channel-url"
                  type="url"
                  value={channelUrl}
                  onChange={(e) => setChannelUrl(e.target.value)}
                  placeholder="https://www.youtube.com/@channelname or https://www.youtube.com/c/channelname"
                  className="w-full px-3 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="grid md:grid-cols-3 gap-4">
                <div>
                  <label htmlFor="video-type" className="block text-sm font-medium mb-2">
                    Video Type
                  </label>
                  <select
                    id="video-type"
                    value={videoType}
                    onChange={(e) => setVideoType(e.target.value)}
                    className="w-full px-3 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {videoTypeOptions.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label htmlFor="language-select" className="block text-sm font-medium mb-2">
                    Language
                  </label>
                  <select
                    id="language-select"
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                    className="w-full px-3 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {languageOptions.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label htmlFor="max-videos" className="block text-sm font-medium mb-2">
                    Max Videos
                  </label>
                  <input
                    id="max-videos"
                    type="number"
                    min="1"
                    max="100"
                    value={maxVideos}
                    onChange={(e) => setMaxVideos(parseInt(e.target.value) || 20)}
                    className="w-full px-3 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <button
                disabled={!channelUrl.trim() || busy}
                onClick={handleStartCrawling}
                className="w-full px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                {busy ? (
                  <>
                    <span className="inline-block animate-spin mr-2">⚪</span>
                    Starting Crawler...
                  </>
                ) : (
                  `🕸️ Start Crawling Channel`
                )}
              </button>

              {/* Demo examples */}
              <div className="mt-6 p-4 bg-gray-50 rounded-md">
                <h3 className="text-sm font-medium text-gray-700 mb-2">📝 Demo Channel Examples:</h3>
                <div className="space-y-2">
                  <button
                    onClick={() => setChannelUrl("https://www.youtube.com/@MrBeast")}
                    className="text-blue-600 hover:underline text-sm block text-left"
                  >
                    @MrBeast - Popular English content
                  </button>
                  <button
                    onClick={() => setChannelUrl("https://www.youtube.com/@VinhVatVo")}
                    className="text-blue-600 hover:underline text-sm block text-left"
                  >
                    @VinhVatVo - Vietnamese tech content
                  </button>
                </div>
              </div>
            </div>
          </div>
        ) : (
          // Results display
          <div className="bg-white border border-gray-200 rounded-lg p-8 shadow-sm">
            {crawlerResult && (
              <>
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-semibold text-gray-900">Crawling Results</h2>
                  <button
                    onClick={resetForm}
                    className="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
                  >
                    🔄 New Crawl
                  </button>
                </div>

                <div className="mb-6 p-4 bg-gray-50 rounded-md">
                  <div className="flex items-center gap-3 mb-3">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${
                        statusColors[crawlerResult.status as keyof typeof statusColors]
                      }`}
                    >
                      <span className="mr-1">{statusIcons[crawlerResult.status as keyof typeof statusIcons]}</span>
                      {crawlerResult.status}
                    </span>
                  </div>
                  
                  <div className="grid md:grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="font-medium text-gray-700">Videos Found:</span>
                      <span className="text-gray-900 ml-1">{crawlerResult.total_videos_found}</span>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">Jobs Created:</span>
                      <span className="text-gray-900 ml-1">{crawlerResult.total_jobs_created}</span>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">Channel:</span>
                      <a
                        href={crawlerResult.channel_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline ml-1 text-xs"
                      >
                        View Channel
                      </a>
                    </div>
                  </div>

                  {crawlerResult.error && (
                    <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-md">
                      <p className="text-sm text-red-700">
                        <strong>Error:</strong> {crawlerResult.error}
                      </p>
                    </div>
                  )}
                </div>

                {/* Jobs list */}
                {crawlerResult.jobs.length > 0 && (
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-4">
                      Transcription Jobs ({crawlerResult.jobs.length})
                    </h3>
                    <div className="space-y-3 max-h-96 overflow-y-auto">
                      {crawlerResult.jobs.map((job) => (
                        <div
                          key={job.job_id}
                          className="flex items-center justify-between p-3 border border-gray-200 rounded-md hover:bg-gray-50"
                        >
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              <span
                                className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                                  statusColors[job.status as keyof typeof statusColors]
                                }`}
                              >
                                {statusIcons[job.status as keyof typeof statusIcons]} {job.status}
                              </span>
                            </div>
                            <h4 className="text-sm font-medium text-gray-900 truncate">
                              {job.title}
                            </h4>
                            <a
                              href={job.video_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-xs text-blue-600 hover:underline truncate block"
                            >
                              {job.video_url}
                            </a>
                          </div>
                          
                          <div className="flex gap-2 ml-4">
                            {job.status === 'done' && (
                              <Link
                                href={`/transcriptions/${job.job_id}`}
                                className="px-3 py-1 bg-green-600 text-white rounded text-xs hover:bg-green-700"
                              >
                                View Result
                              </Link>
                            )}
                            <button
                              onClick={() => navigator.clipboard.writeText(job.job_id)}
                              className="px-3 py-1 bg-gray-100 text-gray-700 rounded text-xs hover:bg-gray-200"
                              title="Copy Job ID"
                            >
                              📋
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="mt-6 flex gap-4">
                  <Link
                    href="/transcriptions"
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                  >
                    📝 View All Jobs
                  </Link>
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}