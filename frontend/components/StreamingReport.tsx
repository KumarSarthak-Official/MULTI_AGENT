import ReactMarkdown from "react-markdown";

interface StreamingReportProps {
  report: string;
  status: "idle" | "running" | "done" | "error";
}

export function StreamingReport({ report, status }: StreamingReportProps) {
  if (status === "idle") {
    return (
      <p className="text-gray-500">
        Submit a research topic to see results here...
      </p>
    );
  }

  if (status === "running" && !report) {
    return (
      <div className="flex items-center gap-2 text-blue-600">
        <div className="animate-spin h-5 w-5 border-2 border-blue-600 border-t-transparent rounded-full"></div>
        <span>Agents are working on your research...</span>
      </div>
    );
  }

  if (status === "done" && report) {
    return (
      <div className="prose prose-sm max-w-none">
        <ReactMarkdown
          components={{
            h1: ({ children }) => (
              <h1 className="text-3xl font-bold mb-4 text-gray-900">
                {children}
              </h1>
            ),
            h2: ({ children }) => (
              <h2 className="text-2xl font-semibold mt-6 mb-3 text-gray-800">
                {children}
              </h2>
            ),
            h3: ({ children }) => (
              <h3 className="text-xl font-semibold mt-4 mb-2 text-gray-800">
                {children}
              </h3>
            ),
            p: ({ children }) => (
              <p className="mb-4 text-gray-700 leading-relaxed">{children}</p>
            ),
            ul: ({ children }) => (
              <ul className="list-disc list-inside mb-4 space-y-2">
                {children}
              </ul>
            ),
            ol: ({ children }) => (
              <ol className="list-decimal list-inside mb-4 space-y-2">
                {children}
              </ol>
            ),
            li: ({ children }) => (
              <li className="text-gray-700">{children}</li>
            ),
            a: ({ href, children }) => (
              <a
                href={href}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800 underline"
              >
                {children}
              </a>
            ),
            code: ({ children }) => (
              <code className="bg-gray-100 px-1 py-0.5 rounded text-sm font-mono text-gray-800">
                {children}
              </code>
            ),
          }}
        >
          {report}
        </ReactMarkdown>
      </div>
    );
  }

  return null;
}
