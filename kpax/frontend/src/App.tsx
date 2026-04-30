import Analyze from "./pages/Analyze";

export default function App() {
  return (
    <div className="min-h-screen bg-[#0a0a0f]">
      <header className="border-b border-zinc-800/50 px-6 py-4">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <h1 className="text-xl font-semibold tracking-tight text-white">KPAX</h1>
            <span className="text-xs text-zinc-500 font-mono mt-0.5">v0.1</span>
          </div>
          <p className="text-xs text-zinc-600 italic hidden sm:block">
            Your life is the sum of your choices.
          </p>
        </div>
      </header>
      <main className="max-w-4xl mx-auto px-6 py-8">
        <Analyze />
      </main>
    </div>
  );
}
