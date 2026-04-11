"use client";

import { useState } from "react";
import { useResearchStream } from "@/hooks/useResearchStream";

export default function Home() {
  const [query, setQuery] = useState("");
  const { report, agentLogs, status, error, startResearch } =
    useResearchStream();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      startResearch(query, false); // Set to false for now since Qdrant isn't running
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

        {/* Agent Logs */}
        {agentLogs.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-xl font-semibold mb-4">Agent Activity</h2>
            <div className="space-y-1 max-h-64 overflow-y-auto">
              {agentLogs.map((log, i) => (
                <div key={i} className="text-sm text-gray-700 font-mono">
                  {log}
                </div>
              ))}
            </div>
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
          {status === "idle" && (
            <p className="text-gray-500">
              Submit a research topic to see results here...
            </p>
          )}
          {status === "running" && (
            <div className="flex items-center gap-2 text-blue-600">
              <div className="animate-spin h-5 w-5 border-2 border-blue-600 border-t-transparent rounded-full"></div>
              <span>Agents are working on your research...</span>
            </div>
          )}
          {status === "done" && report && (
            <div className="prose max-w-none">
              <pre className="whitespace-pre-wrap text-sm">{report}</pre>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
