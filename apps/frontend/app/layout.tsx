// apps/frontend/app/layout.tsx
import "./globals.css";
import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Digital Content Creator",
  description: "YouTube to Text Transcription Service",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <nav className="bg-white border-b border-gray-200 px-4 py-3">
          <div className="container mx-auto flex items-center justify-between">
            <Link href="/" className="text-xl font-bold text-gray-900">
              Digital Content Creator
            </Link>
            <div className="flex space-x-4">
              <Link 
                href="/youtube" 
                className="text-gray-700 hover:text-blue-600 font-medium"
              >
                Create Transcription
              </Link>
              <Link 
                href="/transcriptions" 
                className="text-gray-700 hover:text-blue-600 font-medium"
              >
                View Jobs
              </Link>
              <Link 
                href="/channel-crawler" 
                className="text-gray-700 hover:text-blue-600 font-medium"
              >
                Channel Crawler
              </Link>
            </div>
          </div>
        </nav>
        <main>{children}</main>
      </body>
    </html>
  );
}