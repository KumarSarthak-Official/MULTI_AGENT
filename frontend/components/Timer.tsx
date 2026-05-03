"use client";

import { useEffect, useState } from "react";

interface TimerProps {
  startTime: number | null;
  duration: number | null;
  status: "idle" | "running" | "done" | "error";
}

export function Timer({ startTime, duration, status }: TimerProps) {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    if (status === "running" && startTime) {
      const interval = setInterval(() => {
        setElapsed(Math.floor((Date.now() - startTime) / 1000));
      }, 1000);

      return () => clearInterval(interval);
    } else if (status === "done" && duration) {
      setElapsed(Math.floor(duration));
    }
  }, [status, startTime, duration]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  if (status === "idle") return null;

  return (
    <div className="flex items-center gap-2 text-sm">
      <svg
        className="w-4 h-4 text-gray-500"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
      <span className="text-gray-600">
        {status === "running" && `Elapsed: ${formatTime(elapsed)}`}
        {status === "done" && `Completed in ${formatTime(elapsed)}`}
        {status === "error" && `Failed after ${formatTime(elapsed)}`}
      </span>
      {status === "running" && elapsed > 240 && (
        <span className="text-orange-600 text-xs ml-2">
          (Taking longer than expected...)
        </span>
      )}
    </div>
  );
}
