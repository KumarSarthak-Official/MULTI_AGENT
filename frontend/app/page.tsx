"use client";

import { useState } from "react";
import { useResearchStream } from "@/hooks/useResearchStream";
import { AgentTimeline } from "@/components/AgentTimeline";
import { StreamingReport } from "@/components/StreamingReport";
import { DocumentUpload } from "@/components/DocumentUpload";

export default function Home() {
  const [query, setQuery] = useState("");
  const [showUpload, setShowUpload] = useState(false);
  const { report, agentLogs, status, error, startResearch } =
    useResearchStream();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      startResearch(query, true); // Enable document retrieval
    }
  };

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-6xl mx-auto">
        <header className="mb-8">
          <h1 className="text-4xl font-bold mb-2">
            Multi-Agent Research Platform
          </h1>
          <p className="text-gray-600">
            AI-powered research with 4 specialized agents
          </p>
        </header>

        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <form onSubmit={handleSubmit}>
            <label htmlFor="query" className="block text-sm font-medium mb-2">
              Research Topic
            </label>
            <div className="flex gap-4">
              <input
                id="query"
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="What would you like to research?"
                className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={status === "running"}
              />
              <button
                type="submit"
                disabled={!query.trim() || status === "running"}
                className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                {status === "running" ? "Researching..." : "Research"}
              </button>
            </div>
          </form>
        </div>

        {/* Document Upload Section */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">Upload Documents (Optional)</h2>
            <button
              onClick={() => setShowUpload(!showUpload)}
              className="text-sm text-blue-600 hover:text-blue-700"
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
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-xl font-semibold mb-4">Agent Progress</h2>
            <AgentTimeline agentLogs={agentLogs} status={status} />
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8">
            <p className="text-red-800 font-medium">Error: {error}</p>
          </div>
        )}

        {/* Research Report */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Research Report</h2>
          <StreamingReport report={report} status={status} />
        </div>
      </div>
    </main>
  );
}
