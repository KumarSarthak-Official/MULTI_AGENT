"use client";

import { useState } from "react";

export default function Home() {
  const [query, setQuery] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Research query:", query);
    // SSE hook will be added in Day 11
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
              />
              <button
                type="submit"
                disabled={!query.trim()}
                className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                Research
              </button>
            </div>
          </form>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Research Report</h2>
          <p className="text-gray-500">
            Submit a research topic to see results here...
          </p>
        </div>
      </div>
    </main>
  );
}
