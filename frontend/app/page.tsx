"use client";

import { useState } from "react";
import { useResearchStream } from "@/hooks/useResearchStream";
import { AgentTimeline } from "@/components/AgentTimeline";
import { StreamingReport } from "@/components/StreamingReport";
import { DocumentUpload } from "@/components/DocumentUpload";
import { Timer } from "@/components/Timer";

export default function Home() {
  const [query, setQuery] = useState("");
  const [showUpload, setShowUpload] = useState(false);
  const { report, agentLogs, currentThinking, status, error, startTime, duration, startResearch } =
    useResearchStream();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      startResearch(query, true); // Enable document retrieval
    }
  };

  return (
    <main className="min-h-screen p-8 bg-gradient-to-br from-gray-50 to-blue-50">
      <div className="max-w-7xl mx-auto">
        <header className="mb-8 text-center">
          <h1 className="text-5xl font-bold mb-3 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Multi-Agent Research Platform
          </h1>
          <p className="text-gray-600 text-lg">
            AI-powered research with 4 specialized agents working in real-time
          </p>
        </header>

        <div className="bg-white rounded-xl shadow-lg p-6 mb-8 border border-gray-100">
          <form onSubmit={handleSubmit}>
            <label htmlFor="query" className="block text-sm font-semibold mb-3 text-gray-700">
              What would you like to research?
            </label>
            <div className="flex gap-4">
              <input
                id="query"
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Enter your research topic..."
                className="flex-1 px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                disabled={status === "running"}
              />
              <button
                type="submit"
                disabled={!query.trim() || status === "running"}
                className="px-8 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg hover:from-blue-700 hover:to-purple-700 disabled:from-gray-300 disabled:to-gray-400 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg transform hover:-translate-y-0.5"
              >
                {status === "running" ? (
                  <span className="flex items-center gap-2">
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Researching...
                  </span>
                ) : (
                  "Start Research"
                )}
              </button>
            </div>
          </form>
        </div>

        {/* Document Upload Section */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8 border border-gray-100">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-800">Upload Documents (Optional)</h2>
            <button
              onClick={() => setShowUpload(!showUpload)}
              className="text-sm text-blue-600 hover:text-blue-700 font-medium"
            >
              {showUpload ? "Hide" : "Show"}
            </button>
          </div>
          {showUpload && (
            <DocumentUpload
              onUploadSuccess={(result) => {
                console.log("Upload successful:", result);
              }}
            />
          )}
        </div>

        {/* Agent Timeline */}
        {status !== "idle" && (
          <div className="bg-white rounded-xl shadow-lg p-6 mb-8 border border-gray-100">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-semibold text-gray-800">Agent Progress</h2>
              <Timer startTime={startTime} duration={duration} status={status} />
            </div>
            <AgentTimeline
              agentLogs={agentLogs}
              currentThinking={currentThinking}
              status={status}
            />
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border-2 border-red-200 rounded-xl p-5 mb-8 shadow-md">
            <div className="flex items-start gap-3">
              <svg className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <p className="text-red-800 font-semibold">Error</p>
                <p className="text-red-700">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Research Report */}
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
          <h2 className="text-2xl font-semibold mb-4 text-gray-800">Research Report</h2>
          <StreamingReport report={report} status={status} />
        </div>
      </div>
    </main>
  );
}
