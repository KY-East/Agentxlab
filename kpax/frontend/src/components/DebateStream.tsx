import { useEffect, useRef } from "react";

interface Message {
  agent_name: string;
  content: string;
  round_number: number;
}

interface Props {
  messages: Message[];
  currentRound: number;
  totalRounds: number;
  statusText: string;
}

export default function DebateStream({
  messages,
  currentRound,
  totalRounds,
  statusText,
}: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages.length]);

  const grouped: Record<number, Message[]> = {};
  for (const m of messages) {
    const r = m.round_number || 1;
    if (!grouped[r]) grouped[r] = [];
    grouped[r].push(m);
  }

  return (
    <div className="space-y-6">
      {/* Progress bar */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-xs">
          <span className="text-zinc-500">{statusText}</span>
          <span className="text-kpax-500 font-mono">
            {currentRound > 0 && `${currentRound}/${totalRounds}`}
          </span>
        </div>
        <div className="w-full bg-zinc-800 rounded-full h-1">
          <div
            className="bg-kpax-600 h-1 rounded-full transition-all duration-500"
            style={{
              width: `${totalRounds > 0 ? (currentRound / totalRounds) * 100 : 0}%`,
            }}
          />
        </div>
      </div>

      {/* Messages */}
      <div className="space-y-4 max-h-[60vh] overflow-y-auto pr-2">
        {Object.entries(grouped).map(([round, msgs]) => (
          <div key={round} className="space-y-3">
            <div className="flex items-center gap-2">
              <div className="h-px flex-1 bg-zinc-800" />
              <span className="text-[10px] text-zinc-600 font-mono uppercase">
                Round {round}
              </span>
              <div className="h-px flex-1 bg-zinc-800" />
            </div>
            {msgs.map((msg, i) => (
              <MessageBubble key={`${round}-${i}`} msg={msg} />
            ))}
          </div>
        ))}

        {messages.length === 0 && statusText && (
          <div className="flex items-center justify-center py-16">
            <div className="flex items-center gap-3 text-zinc-500">
              <PulsingDot />
              <span className="text-sm">{statusText}</span>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>
    </div>
  );
}

function MessageBubble({ msg }: { msg: Message }) {
  const isModerator = msg.agent_name === "主持人" || msg.agent_name.toLowerCase().includes("moderator");

  return (
    <div
      className={`rounded-xl p-4 ${
        isModerator
          ? "bg-kpax-600/5 border border-kpax-600/20"
          : "bg-zinc-900/40 border border-zinc-800/50"
      }`}
    >
      <p
        className={`text-xs font-medium mb-2 ${
          isModerator ? "text-kpax-400" : "text-zinc-400"
        }`}
      >
        {msg.agent_name}
      </p>
      <div className="text-sm text-zinc-300 leading-relaxed whitespace-pre-wrap">
        {msg.content}
      </div>
    </div>
  );
}

function PulsingDot() {
  return (
    <span className="flex h-2.5 w-2.5">
      <span className="animate-ping absolute inline-flex h-2.5 w-2.5 rounded-full bg-kpax-500 opacity-75" />
      <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-kpax-600" />
    </span>
  );
}
