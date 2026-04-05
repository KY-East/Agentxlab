import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import i18n from "../i18n";
import { ArrowRight, Loader2 } from "lucide-react";
import { api } from "../api/client";
import type { Discipline } from "../types";

export default function Home() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [fields, setFields] = useState<Discipline[]>([]);
  const [discovering, setDiscovering] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getDisciplines().then((all) => {
      const topLevel = all.filter((d) => !d.parent_id).slice(0, 12);
      setFields(topLevel);
    });
  }, []);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    const q = query.trim();
    if (!q) return;

    setDiscovering(true);
    setError(null);
    try {
      const result = await api.discover(q);
      sessionStorage.setItem("discoveryResult", JSON.stringify(result));
      navigate("/canvas?discover=1");
    } catch (err) {
      setError(err instanceof Error ? err.message : t("home.analyzeFailed"));
    } finally {
      setDiscovering(false);
    }
  };

  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-3xl mx-auto px-6 py-20">
        {/* Hero */}
        <div className="mb-14">
          <h2 className="font-mono text-3xl md:text-4xl font-bold text-white mb-3 tracking-tight">
            {t("home.searchPlaceholder")}
          </h2>
          <p className="text-neutral-500 text-base">
            {t("home.subtitle")}
          </p>
        </div>

        {/* Search */}
        <form onSubmit={handleSearch} className="mb-16">
          <div className="relative">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              disabled={discovering}
              placeholder={t("home.inputPlaceholder")}
              className="w-full px-4 py-3.5 bg-transparent border-2 border-neutral-800 text-white placeholder-neutral-600 focus:outline-none focus:border-cyan-400 text-sm font-mono disabled:opacity-50 transition-colors"
            />
            {query.trim() && (
              <button
                type="submit"
                disabled={discovering}
                className="absolute right-2 top-1/2 -translate-y-1/2 px-3 py-1.5 bg-cyan-400 text-black font-mono text-xs font-bold uppercase tracking-wider hover:bg-cyan-300 disabled:opacity-50 transition-colors"
              >
                {discovering ? (
                  <Loader2 size={14} className="animate-spin" />
                ) : (
                  <ArrowRight size={14} />
                )}
              </button>
            )}
          </div>
          {discovering && (
            <p className="font-mono text-xs text-cyan-400 mt-3 animate-blink">
              [{t("home.analyzing")}]
            </p>
          )}
          {error && (
            <p className="font-mono text-xs text-red-500 mt-3">{error}</p>
          )}
        </form>

        {/* Discipline tags */}
        <section className="mb-14">
          <h3 className="font-mono text-[10px] uppercase tracking-[0.2em] text-neutral-600 mb-4">
            {t("home.hotDisciplines")}
          </h3>
          <div className="flex flex-wrap gap-2">
            {fields.map((f) => (
              <button
                key={f.id}
                onClick={() => navigate(`/canvas?field=${f.id}`)}
                className="px-3 py-1.5 border border-neutral-700 text-xs text-neutral-400 hover:border-cyan-400 hover:text-cyan-400 transition-colors font-mono"
              >
                {i18n.language?.startsWith("zh") ? (f.name_zh || f.name_en) : f.name_en}
              </button>
            ))}
          </div>
        </section>

        {/* Feature cards */}
        <section>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-0 md:gap-0 border-2 border-neutral-800">
            <FeatureCard
              title={t("home.featureDiscovery")}
              desc={t("home.featureDiscoveryDesc")}
              onClick={() => navigate("/canvas")}
              border="md:border-r-2 border-b-2 md:border-b-0 border-neutral-800"
            />
            <FeatureCard
              title={t("home.featureDebate")}
              desc={t("home.featureDebateDesc")}
              onClick={() => navigate("/debate")}
              border="md:border-r-2 border-b-2 md:border-b-0 border-neutral-800"
            />
            <FeatureCard
              title={t("home.featureForum")}
              desc={t("home.featureForumDesc")}
              onClick={() => navigate("/forum")}
              border=""
            />
          </div>
        </section>
      </div>
    </div>
  );
}

function FeatureCard({
  title,
  desc,
  onClick,
  border,
}: {
  title: string;
  desc: string;
  onClick: () => void;
  border: string;
}) {
  return (
    <button
      onClick={onClick}
      className={`flex flex-col items-start gap-2 p-5 hover:bg-neutral-900 transition-colors text-left group ${border}`}
    >
      <h4 className="font-mono text-sm font-bold text-white uppercase tracking-wider group-hover:text-cyan-400 transition-colors">
        {title}
      </h4>
      <p className="text-xs text-neutral-500">{desc}</p>
    </button>
  );
}
