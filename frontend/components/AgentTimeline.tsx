interface AgentTimelineProps {
  agentLogs: string[];
  status: "idle" | "running" | "done" | "error";
}

type AgentStatus = "pending" | "running" | "done";

interface Agent {
  name: string;
  label: string;
  status: AgentStatus;
}

export function AgentTimeline({ agentLogs, status }: AgentTimelineProps) {
  // Determine agent statuses based on logs
  const agents: Agent[] = [
    { name: "search", label: "Search Agent", status: "pending" },
    { name: "rag", label: "RAG Agent", status: "pending" },
    { name: "synthesis", label: "Synthesis Agent", status: "pending" },
    { name: "critique", label: "Critique Agent", status: "pending" },
  ];

  // Update agent statuses based on logs
  agentLogs.forEach((log) => {
    if (log.includes("Search Agent:")) {
      const searchAgent = agents.find((a) => a.name === "search");
      if (searchAgent && searchAgent.status === "pending") {
        searchAgent.status = "running";
      }
      if (log.includes("Returning") && searchAgent) {
        searchAgent.status = "done";
      }
    }
    if (log.includes("RAG Agent:")) {
      const ragAgent = agents.find((a) => a.name === "rag");
      if (ragAgent && ragAgent.status === "pending") {
        ragAgent.status = "running";
      }
      if (
        (log.includes("Returning") || log.includes("No documents")) &&
        ragAgent
      ) {
        ragAgent.status = "done";
      }
    }
    if (log.includes("Synthesis Agent:")) {
      const synthesisAgent = agents.find((a) => a.name === "synthesis");
      if (synthesisAgent && synthesisAgent.status === "pending") {
        synthesisAgent.status = "running";
      }
      if (log.includes("Generated report") && synthesisAgent) {
        synthesisAgent.status = "done";
      }
    }
    if (log.includes("Critique Agent:")) {
      const critiqueAgent = agents.find((a) => a.name === "critique");
      if (critiqueAgent && critiqueAgent.status === "pending") {
        critiqueAgent.status = "running";
      }
      if (
        (log.includes("finalizing") || log.includes("Score meets")) &&
        critiqueAgent
      ) {
        critiqueAgent.status = "done";
      }
    }
  });

  // If overall status is done, mark all as done
  if (status === "done") {
    agents.forEach((agent) => {
      if (agent.status === "running") {
        agent.status = "done";
      }
    });
  }

  return (
    <div className="space-y-4">
      {agents.map((agent, index) => (
        <div key={agent.name} className="flex items-start gap-4">
          {/* Status indicator */}
          <div className="flex flex-col items-center">
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center ${
                agent.status === "pending"
                  ? "bg-gray-200"
                  : agent.status === "running"
                  ? "bg-blue-500 animate-pulse"
                  : "bg-green-500"
              }`}
            >
              {agent.status === "done" && (
                <svg
                  className="w-5 h-5 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              )}
            </div>
            {/* Connector line */}
            {index < agents.length - 1 && (
              <div className="w-0.5 h-12 bg-gray-200 mt-2"></div>
            )}
          </div>

          {/* Agent label */}
          <div className="flex-1 pt-1">
            <h3
              className={`font-medium ${
                agent.status === "running"
                  ? "text-blue-600"
                  : agent.status === "done"
                  ? "text-green-600"
                  : "text-gray-500"
              }`}
            >
              {agent.label}
            </h3>
            <p className="text-sm text-gray-500">
              {agent.status === "pending" && "Waiting..."}
              {agent.status === "running" && "Processing..."}
              {agent.status === "done" && "Complete"}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}
