"use client";

"use client";
import { useState, useEffect } from "react";
import Link from 'next/link';

interface Transcription {
  id: string;
  status: 'queued' | 'processing' | 'done' | 'error';
  title?: string;
  youtube_url?: string;
  file_url?: string;
  language?: string;
  engine?: string;
  created_at: string;
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

export default function TranscriptionsList() {
  const [transcriptions, setTranscriptions] = useState<Transcription[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<string>('all');
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);

  const loadTranscriptions = async (reset = false) => {
    try {
      setLoading(true);
      const offset = reset ? 0 : (page - 1) * 20;
      const statusParam = filter === 'all' ? '' : `&status=${filter}`;
      
      const response = await fetch(`/api/transcriptions?limit=20&offset=${offset}${statusParam}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (reset) {
        setTranscriptions(data);
        setPage(1);
      } else {
        setTranscriptions(prev => [...prev, ...data]);
      }
      
      setHasMore(data.length === 20);
      setError(null);
    } catch (err) {
      console.error('Error loading transcriptions:', err);
      setError('Failed to load transcriptions');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTranscriptions(true);
  }, [filter]);

  const loadMore = () => {
    setPage(prev => prev + 1);
    loadTranscriptions();
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('vi-VN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const refresh = () => {
    setPage(1);
    loadTranscriptions(true);
  };

  if (loading && transcriptions.length === 0) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading transcriptions...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Transcription Jobs</h1>
        <p className="text-gray-600">Manage and view all your transcription jobs</p>
      </div>

      {/* Controls */}
      <div className="mb-6 flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <div className="flex gap-2 items-center">
          <label htmlFor="status-filter" className="text-sm font-medium text-gray-700">
            Filter by status:
          </label>
          <select
            id="status-filter"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="all">All Status</option>
            <option value="queued">Queued</option>
            <option value="processing">Processing</option>
            <option value="done">Completed</option>
            <option value="error">Error</option>
          </select>
        </div>

        <div className="flex gap-2">
          <button
            onClick={refresh}
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors text-sm font-medium"
          >
            🔄 Refresh
          </button>
          <Link 
            href="/youtube"
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm font-medium"
          >
            + New Transcription
          </Link>
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-red-700">{error}</p>
          <button
            onClick={() => loadTranscriptions(true)}
            className="mt-2 text-red-600 hover:text-red-800 text-sm font-medium"
          >
            Try again
          </button>
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && transcriptions.length === 0 && (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">📝</div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No transcriptions yet</h3>
          <p className="text-gray-600 mb-6">Get started by creating your first transcription</p>
          <Link 
            href="/youtube"
            className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors font-medium"
          >
            Create Transcription
          </Link>
        </div>
      )}

      {/* Transcriptions List */}
      {transcriptions.length > 0 && (
        <div className="space-y-4">
          {transcriptions.map((transcription) => (
            <div
              key={transcription.id}
              className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  {/* Header */}
                  <div className="flex items-center gap-3 mb-3">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${
                        statusColors[transcription.status]
                      }`}
                    >
                      <span className="mr-1">{statusIcons[transcription.status]}</span>
                      {transcription.status}
                    </span>
                    <span className="text-sm text-gray-500">
                      {formatDate(transcription.created_at)}
                    </span>
                  </div>

                  {/* Title */}
                  <h3 className="text-lg font-semibold text-gray-900 mb-2 truncate">
                    {transcription.title || 'Untitled Transcription'}
                  </h3>

                  {/* YouTube URL */}
                  {transcription.youtube_url && (
                    <div className="mb-3">
                      <a
                        href={transcription.youtube_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-800 text-sm truncate block"
                      >
                        🎬 {transcription.youtube_url}
                      </a>
                    </div>
                  )}

                  {/* Metadata */}
                  <div className="flex flex-wrap gap-4 text-sm text-gray-500 mb-3">
                    {transcription.language && (
                      <span>🌐 Language: {transcription.language}</span>
                    )}
                    {transcription.engine && (
                      <span>⚙️ Engine: {transcription.engine}</span>
                    )}
                  </div>

                  {/* Error Message */}
                  {transcription.status === 'error' && transcription.error && (
                    <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-md">
                      <p className="text-sm text-red-700">
                        <strong>Error:</strong> {transcription.error}
                      </p>
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="flex flex-col gap-2 ml-4">
                  {transcription.status === 'done' && (
                    <Link
                      href={`/transcriptions/${transcription.id}`}
                      className="px-3 py-1.5 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm font-medium text-center"
                    >
                      View Result
                    </Link>
                  )}
                  
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(transcription.id);
                      // You could add a toast notification here
                    }}
                    className="px-3 py-1.5 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors text-sm"
                    title="Copy Job ID"
                  >
                    📋 Copy ID
                  </button>
                </div>
              </div>
            </div>
          ))}

          {/* Load More */}
          {hasMore && (
            <div className="text-center pt-6">
              <button
                onClick={loadMore}
                disabled={loading}
                className="px-6 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors font-medium disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <span className="inline-block animate-spin mr-2">⚪</span>
                    Loading...
                  </>
                ) : (
                  'Load More'
                )}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}