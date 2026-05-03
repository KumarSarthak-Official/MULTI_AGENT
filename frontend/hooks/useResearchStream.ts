import { useState, useCallback } from "react";
import { API_URL } from "@/lib/config";

type ResearchStatus = "idle" | "running" | "done" | "error";

interface UseResearchStreamReturn {
  report: string;
  agentLogs: string[];
  status: ResearchStatus;
  error: string | null;
  startResearch: (query: string, useDocuments?: boolean) => void;
}

export function useResearchStream(): UseResearchStreamReturn {
  const [report, setReport] = useState("");
  const [agentLogs, setAgentLogs] = useState<string[]>([]);
  const [status, setStatus] = useState<ResearchStatus>("idle");
  const [error, setError] = useState<string | null>(null);

  const startResearch = useCallback(
    (query: string, useDocuments: boolean = true) => {
      // Reset state
      setReport("");
      setAgentLogs([]);
      setError(null);
      setStatus("running");

      // Create EventSource connection
      const eventSource = new EventSource(
        `${API_URL}/api/v1/research/stream?${new URLSearchParams({
          query,
          use_documents: String(useDocuments),
        })}`
      );

      // Handle different event types
      eventSource.addEventListener("start", (event: Event) => {
        const data = JSON.parse((event as MessageEvent).data);
        console.log("Research started:", data);
      });

      eventSource.addEventListener("node_complete", (event: Event) => {
        const data = JSON.parse((event as MessageEvent).data);
        const { node, logs } = data;

        // Add logs to state
        setAgentLogs((prev) => [...prev, ...logs]);
        console.log(`${node} completed:`, logs);
      });

      eventSource.addEventListener("complete", (event: Event) => {
        const data = JSON.parse((event as MessageEvent).data);
        const { final_report } = data;

        setReport(final_report);
        setStatus("done");
        eventSource.close();
        console.log("Research complete:", data);
      });

      eventSource.addEventListener("error", (event: Event) => {
        const data = JSON.parse((event as MessageEvent).data);
        setError(data.message);
        setStatus("error");
        eventSource.close();
        console.error("Research error:", data);
      });

      // Handle connection errors
      eventSource.onerror = (err) => {
        console.error("EventSource error:", err);
        setError("Connection error. Please check if the backend is running.");
        setStatus("error");
        eventSource.close();
      };
    },
    []
  );

  return {
    report,
    agentLogs,
    status,
    error,
    startResearch,
  };
}
