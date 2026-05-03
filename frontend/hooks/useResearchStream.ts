import { useState, useCallback } from "react";
import { API_URL } from "@/lib/config";

type ResearchStatus = "idle" | "running" | "done" | "error";

interface UseResearchStreamReturn {
  report: string;
  agentLogs: string[];
  currentThinking: { node: string; message: string } | null;
  status: ResearchStatus;
  error: string | null;
  startTime: number | null;
  duration: number | null;
  startResearch: (query: string, useDocuments?: boolean) => void;
}

export function useResearchStream(): UseResearchStreamReturn {
  const [report, setReport] = useState("");
  const [agentLogs, setAgentLogs] = useState<string[]>([]);
  const [currentThinking, setCurrentThinking] = useState<{ node: string; message: string } | null>(null);
  const [status, setStatus] = useState<ResearchStatus>("idle");
  const [error, setError] = useState<string | null>(null);
  const [startTime, setStartTime] = useState<number | null>(null);
  const [duration, setDuration] = useState<number | null>(null);

  const startResearch = useCallback(
    (query: string, useDocuments: boolean = true) => {
      // Reset state
      setReport("");
      setAgentLogs([]);
      setCurrentThinking(null);
      setError(null);
      setStatus("running");
      setStartTime(Date.now());
      setDuration(null);

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

      eventSource.addEventListener("node_start", (event: Event) => {
        const data = JSON.parse((event as MessageEvent).data);
        console.log(`Node started: ${data.node}`);
        setCurrentThinking({ node: data.node, message: "Starting..." });
      });

      eventSource.addEventListener("thinking", (event: Event) => {
        const data = JSON.parse((event as MessageEvent).data);
        const { node, message } = data;

        // Update current thinking in real-time
        setCurrentThinking({ node, message });

        // Add to logs
        setAgentLogs((prev) => [...prev, message]);
        console.log(`${node} thinking:`, message);
      });

      eventSource.addEventListener("node_complete", (event: Event) => {
        const data = JSON.parse((event as MessageEvent).data);
        const { node, logs } = data;

        // Clear current thinking for this node
        setCurrentThinking(null);
        console.log(`${node} completed:`, logs);
      });

      eventSource.addEventListener("complete", (event: Event) => {
        const data = JSON.parse((event as MessageEvent).data);
        const { final_report, duration_seconds } = data;

        setReport(final_report);
        setStatus("done");
        setDuration(duration_seconds);
        setCurrentThinking(null);
        eventSource.close();
        console.log("Research complete:", data);
      });

      eventSource.addEventListener("error", (event: Event) => {
        try {
          const messageEvent = event as MessageEvent;
          if (messageEvent.data) {
            const data = JSON.parse(messageEvent.data);
            setError(data.message || "An error occurred");
            console.error("Research error:", data);
          } else {
            setError("Connection error. Please check if the backend is running.");
          }
        } catch (e) {
          setError("An unknown error occurred");
        }
        setStatus("error");
        setDuration((Date.now() - (startTime || Date.now())) / 1000);
        setCurrentThinking(null);
        eventSource.close();
      });

      // Handle connection errors
      eventSource.onerror = (err) => {
        console.error("EventSource error:", err);
        setError("Connection error. Please check if the backend is running.");
        setStatus("error");
        setDuration((Date.now() - (startTime || Date.now())) / 1000);
        setCurrentThinking(null);
        eventSource.close();
      };
    },
    []
  );

  return {
    report,
    agentLogs,
    currentThinking,
    status,
    error,
    startTime,
    duration,
    startResearch,
  };
}
