import Link from "next/link";

export default function Home() {
  return (
    <div className="container mx-auto px-4 py-12 text-center">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-5xl font-bold text-gray-900 mb-6">
          Digital Content Creator
        </h1>
        <p className="text-xl text-gray-600 mb-12">
          Transform your YouTube videos into accurate transcriptions with AI-powered speech recognition
        </p>

        <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
          <Link 
            href="/youtube"
            className="group bg-blue-600 text-white p-8 rounded-xl shadow-lg hover:bg-blue-700 transition-all duration-300 hover:scale-105"
          >
            <div className="text-4xl mb-4">🎬</div>
            <h3 className="text-xl font-semibold mb-2">Create Transcription</h3>
            <p className="text-blue-100">
              Paste a YouTube URL and get accurate transcriptions with language optimization
            </p>
          </Link>

          <Link 
            href="/transcriptions"
            className="group bg-gray-800 text-white p-8 rounded-xl shadow-lg hover:bg-gray-900 transition-all duration-300 hover:scale-105"
          >
            <div className="text-4xl mb-4">📝</div>
            <h3 className="text-xl font-semibold mb-2">View Your Jobs</h3>
            <p className="text-gray-300">
              Track progress and manage all your transcription jobs in one place
            </p>
          </Link>

          <Link 
            href="/channel-crawler"
            className="group bg-green-600 text-white p-8 rounded-xl shadow-lg hover:bg-green-700 transition-all duration-300 hover:scale-105"
          >
            <div className="text-4xl mb-4">📺</div>
            <h3 className="text-xl font-semibold mb-2">Channel Crawler</h3>
            <p className="text-green-100">
              Transcribe all videos from a YouTube channel automatically
            </p>
          </Link>
        </div>

        <div className="mt-16 text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-8">Features</h2>
          <div className="grid md:grid-cols-3 gap-6 text-left">
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <div className="text-2xl mb-3">🌍</div>
              <h3 className="font-semibold text-gray-900 mb-2">Multi-Language Support</h3>
              <p className="text-gray-600 text-sm">
                Supports Vietnamese, English, Chinese, Japanese with optimized accuracy
              </p>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <div className="text-2xl mb-3">⚡</div>
              <h3 className="font-semibold text-gray-900 mb-2">Fast Processing</h3>
              <p className="text-gray-600 text-sm">
                Advanced chunked processing for videos up to 2 hours long
              </p>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <div className="text-2xl mb-3">📊</div>
              <h3 className="font-semibold text-gray-900 mb-2">Progress Tracking</h3>
              <p className="text-gray-600 text-sm">
                Real-time status updates and comprehensive job management
              </p>
            </div>
          </div>
        </div>
        
        <div className="mt-16 p-6 bg-gray-50 rounded-xl">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Legacy File Upload</h3>
          <p className="text-gray-600 mb-4">Still need to upload audio files directly?</p>
          <Link 
            href="/legacy-upload"
            className="inline-block px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
          >
            Upload Audio Files
          </Link>
        </div>
      </div>
    </div>
  );
}