"use client";

import { useState } from "react";

interface AgentTimelineProps {
  agentLogs: string[];
  currentThinking: { node: string; message: string } | null;
  status: "idle" | "running" | "done" | "error";
}

type AgentStatus = "pending" | "running" | "done";

interface Agent {
  name: string;
  label: string;
  status: AgentStatus;
  logs: string[];
  icon: string;
  description: string;
  color: string;
}

export function AgentTimeline({ agentLogs, currentThinking, status }: AgentTimelineProps) {
  const [expandedAgent, setExpandedAgent] = useState<string | null>(null);

  // Define agents with descriptions and colors
  const agents: Agent[] = [
    {
      name: "search",
      label: "Search Agent",
      status: "pending",
      logs: [],
      icon: "🔍",
      description: "Searching the web for relevant information",
      color: "blue",
    },
    {
      name: "rag",
      label: "RAG Agent",
      status: "pending",
      logs: [],
      icon: "📚",
      description: "Retrieving relevant documents from knowledge base",
      color: "purple",
    },
    {
      name: "synthesis",
      label: "Synthesis Agent",
      status: "pending",
      logs: [],
      icon: "✍️",
      description: "Synthesizing information into a comprehensive report",
      color: "green",
    },
    {
      name: "critique",
      label: "Critique Agent",
      status: "pending",
      logs: [],
      icon: "🔬",
      description: "Evaluating report quality and accuracy",
      color: "orange",
    },
  ];

  // Parse logs and assign to agents
  agentLogs.forEach((log) => {
    if (log.includes("Search Agent:")) {
      const searchAgent = agents.find((a) => a.name === "search");
      if (searchAgent) {
        searchAgent.logs.push(log.replace("Search Agent: ", ""));
        if (searchAgent.status === "pending") {
          searchAgent.status = "running";
        }
        if (log.includes("Returning")) {
          searchAgent.status = "done";
        }
      }
    } else if (log.includes("RAG Agent:")) {
      const ragAgent = agents.find((a) => a.name === "rag");
      if (ragAgent) {
        ragAgent.logs.push(log.replace("RAG Agent: ", ""));
        if (ragAgent.status === "pending") {
          ragAgent.status = "running";
        }
        if (log.includes("Returning") || log.includes("No documents")) {
          ragAgent.status = "done";
        }
      }
    } else if (log.includes("Synthesis Agent:")) {
      const synthesisAgent = agents.find((a) => a.name === "synthesis");
      if (synthesisAgent) {
        synthesisAgent.logs.push(log.replace("Synthesis Agent: ", ""));
        if (synthesisAgent.status === "pending") {
          synthesisAgent.status = "running";
        }
        if (log.includes("Generated report")) {
          synthesisAgent.status = "done";
        }
      }
    } else if (log.includes("Critique Agent:")) {
      const critiqueAgent = agents.find((a) => a.name === "critique");
      if (critiqueAgent) {
        critiqueAgent.logs.push(log.replace("Critique Agent: ", ""));
        if (critiqueAgent.status === "pending") {
          critiqueAgent.status = "running";
        }
        if (log.includes("finalizing") || log.includes("Score meets")) {
          critiqueAgent.status = "done";
        }
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

  // Calculate progress percentage
  const completedAgents = agents.filter((a) => a.status === "done").length;
  const progressPercentage = (completedAgents / agents.length) * 100;

  const getColorClasses = (color: string, variant: "bg" | "border" | "text" | "gradient") => {
    const colors: Record<string, Record<string, string>> = {
      blue: {
        bg: "bg-blue-500",
        border: "border-blue-500",
        text: "text-blue-700",
        gradient: "bg-gradient-to-r from-blue-50 to-blue-100",
      },
      purple: {
        bg: "bg-purple-500",
        border: "border-purple-500",
        text: "text-purple-700",
        gradient: "bg-gradient-to-r from-purple-50 to-purple-100",
      },
      green: {
        bg: "bg-green-500",
        border: "border-green-500",
        text: "text-green-700",
        gradient: "bg-gradient-to-r from-green-50 to-green-100",
      },
      orange: {
        bg: "bg-orange-500",
        border: "border-orange-500",
        text: "text-orange-700",
        gradient: "bg-gradient-to-r from-orange-50 to-orange-100",
      },
    };
    return colors[color]?.[variant] || colors.blue[variant];
  };

  return (
    <div className="space-y-6">
      {/* Progress Bar */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm text-gray-600">
          <span className="font-medium">Overall Progress</span>
          <span>
            {completedAgents} / {agents.length} agents completed
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden shadow-inner">
          <div
            className="bg-gradient-to-r from-blue-500 to-purple-500 h-3 rounded-full transition-all duration-500 ease-out"
            style={{ width: `${progressPercentage}%` }}
          />
        </div>
      </div>

      {/* Agent Cards */}
      <div className="space-y-4">
        {agents.map((agent, index) => {
          const isCurrentlyThinking = currentThinking?.node === agent.name;
          const isActive = agent.status === "running" || isCurrentlyThinking;

          return (
            <div
              key={agent.name}
              className={`border-2 rounded-xl overflow-hidden transition-all duration-300 ${
                isActive
                  ? `${getColorClasses(agent.color, "border")} shadow-lg scale-[1.02]`
                  : agent.status === "done"
                  ? "border-green-300 shadow-md"
                  : "border-gray-200"
              }`}
            >
              {/* Agent Header */}
              <div
                className={`p-5 cursor-pointer transition-colors ${
                  isActive
                    ? getColorClasses(agent.color, "gradient")
                    : agent.status === "done"
                    ? "bg-green-50"
                    : "bg-gray-50"
                }`}
                onClick={() =>
                  setExpandedAgent(expandedAgent === agent.name ? null : agent.name)
                }
              >
                <div className="flex items-center gap-4">
                  {/* Status Indicator */}
                  <div className="flex-shrink-0">
                    {agent.status === "pending" && (
                      <div className="w-10 h-10 rounded-full bg-gray-300 flex items-center justify-center text-xl shadow-sm">
                        {agent.icon}
                      </div>
                    )}
                    {isActive && (
                      <div className={`w-10 h-10 rounded-full ${getColorClasses(agent.color, "bg")} flex items-center justify-center shadow-lg`}>
                        <div className="w-5 h-5 border-3 border-white border-t-transparent rounded-full animate-spin" />
                      </div>
                    )}
                    {agent.status === "done" && !isActive && (
                      <div className="w-10 h-10 rounded-full bg-green-500 flex items-center justify-center shadow-lg">
                        <svg
                          className="w-6 h-6 text-white"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={3}
                            d="M5 13l4 4L19 7"
                          />
                        </svg>
                      </div>
                    )}
                  </div>

                  {/* Agent Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-1">
                      <h3
                        className={`font-bold text-lg ${
                          isActive
                            ? getColorClasses(agent.color, "text")
                            : agent.status === "done"
                            ? "text-green-700"
                            : "text-gray-500"
                        }`}
                      >
                        {agent.label}
                      </h3>
                      {isActive && (
                        <span className={`px-3 py-1 text-xs font-semibold ${getColorClasses(agent.color, "bg")} text-white rounded-full shadow-sm animate-pulse`}>
                          Working...
                        </span>
                      )}
                      {agent.status === "done" && !isActive && (
                        <span className="px-3 py-1 text-xs font-semibold bg-green-500 text-white rounded-full shadow-sm">
                          ✓ Complete
                        </span>
                      )}
                    </div>

                    {/* Current Thinking Display - Like Claude/ChatGPT */}
                    {isCurrentlyThinking && currentThinking && (
                      <div className="mt-2 p-3 bg-white rounded-lg border-l-4 border-blue-500 shadow-sm">
                        <div className="flex items-start gap-2">
                          <div className="flex-shrink-0 mt-1">
                            <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
                          </div>
                          <p className="text-sm text-gray-700 italic">
                            {currentThinking.message}
                          </p>
                        </div>
                      </div>
                    )}

                    {!isCurrentlyThinking && (
                      <p className="text-sm text-gray-600">
                        {agent.status === "pending" && "Waiting to start..."}
                        {agent.status === "running" && agent.description}
                        {agent.status === "done" &&
                          agent.logs.length > 0 &&
                          agent.logs[agent.logs.length - 1]}
                      </p>
                    )}
                  </div>

                  {/* Expand Icon */}
                  {agent.logs.length > 0 && (
                    <div className="flex-shrink-0">
                      <svg
                        className={`w-6 h-6 text-gray-400 transition-transform ${
                          expandedAgent === agent.name ? "rotate-180" : ""
                        }`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M19 9l-7 7-7-7"
                        />
                      </svg>
                    </div>
                  )}
                </div>
              </div>

              {/* Expanded Logs */}
              {expandedAgent === agent.name && agent.logs.length > 0 && (
                <div className="p-5 bg-white border-t-2 border-gray-100">
                  <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    Activity Log
                  </h4>
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {agent.logs.map((log, idx) => (
                      <div
                        key={idx}
                        className="text-sm text-gray-600 flex items-start gap-3 p-2 hover:bg-gray-50 rounded transition-colors"
                      >
                        <span className="text-gray-400 flex-shrink-0 font-mono text-xs mt-0.5">
                          {String(idx + 1).padStart(2, "0")}
                        </span>
                        <span className="flex-1">{log}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
