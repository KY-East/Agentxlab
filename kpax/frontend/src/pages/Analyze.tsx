import { useState, useCallback } from "react";
import api, {
  type StartResponse,
  type ContextResponse,
  type StreamEvent,
  type ReportData,
} from "../api/client";
import QuestionInput from "../components/QuestionInput";
import ContextForm from "../components/ContextForm";
import AnalysisPreview from "../components/AnalysisPreview";
import DebateStream from "../components/DebateStream";
import Report from "../components/Report";

type Stage = "idle" | "collecting_context" | "previewing" | "debating" | "report_ready";

interface DebateMessage {
  agent_name: string;
  content: string;
  round_number: number;
}

export default function Analyze() {
  const [stage, setStage] = useState<Stage>("idle");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [sessionId, setSessionId] = useState("");
  const [startData, setStartData] = useState<StartResponse | null>(null);
  const [contextData, setContextData] = useState<ContextResponse | null>(null);
  const [debateMessages, setDebateMessages] = useState<DebateMessage[]>([]);
  const [currentRound, setCurrentRound] = useState(0);
  const [totalRounds, setTotalRounds] = useState(3);
  const [statusText, setStatusText] = useState("");
  const [report, setReport] = useState<ReportData | null>(null);

  const handleQuestionSubmit = useCallback(async (question: string) => {
    setLoading(true);
    setError("");
    try {
      const data = await api.startAnalysis(question);
      setSessionId(data.session_id);
      setStartData(data);
      setStage("collecting_context");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }, []);

  const handleContextSubmit = useCallback(
    async (answers: Record<string, unknown>) => {
      setLoading(true);
      setError("");
      try {
        const data = await api.submitContext(sessionId, answers);
        setContextData(data);
        setStage("previewing");
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : "Something went wrong");
      } finally {
        setLoading(false);
      }
    },
    [sessionId]
  );

  const handleSupplement = useCallback(
    async (text: string) => {
      try {
        await api.supplement(sessionId, text);
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : "Something went wrong");
      }
    },
    [sessionId]
  );

  const handleStartDebate = useCallback(async () => {
    setStage("debating");
    setDebateMessages([]);
    setCurrentRound(0);
    setStatusText("Starting analysis...");
    setError("");

    try {
      const res = await api.runAnalysis(sessionId);
      if (!res.ok || !res.body) {
        throw new Error("Failed to start analysis stream");
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const raw = line.slice(6).trim();
          if (!raw) continue;

          try {
            const event: StreamEvent = JSON.parse(raw);

            switch (event.type) {
              case "round_start":
                setCurrentRound(event.round || 0);
                setTotalRounds(event.total_rounds || 3);
                setStatusText(`Round ${event.round} / ${event.total_rounds}`);
                break;

              case "message":
                setDebateMessages((prev) => [
                  ...prev,
                  {
                    agent_name: event.agent_name || "",
                    content: event.content || "",
                    round_number: event.round_number || 0,
                  },
                ]);
                break;

              case "generating_summary":
                setStatusText("Generating summary...");
                break;

              case "generating_report":
                setStatusText("Building your report...");
                break;

              case "done":
                if (event.report) {
                  setReport(event.report);
                }
                setStage("report_ready");
                setStatusText("");
                break;

              case "error":
                setError(event.error || "Analysis failed");
                break;
            }
          } catch {
            // skip malformed SSE
          }
        }
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Analysis stream failed");
    }
  }, [sessionId]);

  const handleReset = useCallback(() => {
    setStage("idle");
    setSessionId("");
    setStartData(null);
    setContextData(null);
    setDebateMessages([]);
    setReport(null);
    setError("");
    setStatusText("");
  }, []);

  return (
    <div className="space-y-6">
      {/* Progress indicator */}
      <StepIndicator stage={stage} />

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg px-4 py-3 text-sm text-red-400">
          {error}
        </div>
      )}

      {stage === "idle" && (
        <QuestionInput onSubmit={handleQuestionSubmit} loading={loading} />
      )}

      {stage === "collecting_context" && startData && (
        <ContextForm
          questionSummary={startData.question_summary}
          fields={startData.context_fields}
          onSubmit={handleContextSubmit}
          loading={loading}
        />
      )}

      {stage === "previewing" && contextData && (
        <AnalysisPreview
          experts={contextData.experts}
          analysisAngles={contextData.analysis_angles}
          coreTension={contextData.core_tension}
          onSupplement={handleSupplement}
          onStart={handleStartDebate}
        />
      )}

      {stage === "debating" && (
        <DebateStream
          messages={debateMessages}
          currentRound={currentRound}
          totalRounds={totalRounds}
          statusText={statusText}
        />
      )}

      {stage === "report_ready" && report && (
        <Report
          report={report}
          sessionId={sessionId}
          onReset={handleReset}
        />
      )}
    </div>
  );
}

function StepIndicator({ stage }: { stage: Stage }) {
  const steps = [
    { key: "idle", label: "Question" },
    { key: "collecting_context", label: "Context" },
    { key: "previewing", label: "Preview" },
    { key: "debating", label: "Analysis" },
    { key: "report_ready", label: "Report" },
  ];
  const currentIdx = steps.findIndex((s) => s.key === stage);

  return (
    <div className="flex items-center gap-1 mb-8">
      {steps.map((step, i) => {
        const isActive = i === currentIdx;
        const isDone = i < currentIdx;
        return (
          <div key={step.key} className="flex items-center gap-1">
            <div
              className={`
                flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium transition-all
                ${isActive ? "bg-kpax-600/20 text-kpax-400 ring-1 ring-kpax-600/30" : ""}
                ${isDone ? "text-kpax-600" : ""}
                ${!isActive && !isDone ? "text-zinc-600" : ""}
              `}
            >
              <span
                className={`
                  w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-mono
                  ${isActive ? "bg-kpax-600 text-white" : ""}
                  ${isDone ? "bg-kpax-900/50 text-kpax-400" : ""}
                  ${!isActive && !isDone ? "bg-zinc-800 text-zinc-600" : ""}
                `}
              >
                {isDone ? "\u2713" : i + 1}
              </span>
              <span className="hidden sm:inline">{step.label}</span>
            </div>
            {i < steps.length - 1 && (
              <div
                className={`w-6 h-px ${i < currentIdx ? "bg-kpax-700" : "bg-zinc-800"}`}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}
