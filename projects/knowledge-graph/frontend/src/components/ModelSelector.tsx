import { useState, useEffect, useCallback } from "react";
import { useTranslation } from "react-i18next";
import { Cpu } from "lucide-react";
import { api } from "../api/client";
import type { SubscriptionInfo } from "../types";

interface Props {
  className?: string;
}

export default function ModelSelector({ className = "" }: Props) {
  const { t } = useTranslation();
  const [sub, setSub] = useState<SubscriptionInfo | null>(null);

  const load = useCallback(async () => {
    try {
      const res = await api.getMySubscription();
      setSub(res);
    } catch {
      setSub(null);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  if (!sub || sub.allowed_models.length <= 1) return null;

  return (
    <div className={`flex items-center gap-1.5 ${className}`}>
      <Cpu size={10} className="text-neutral-600 shrink-0" />
      <select
        value={sub.preferred_model || ""}
        onChange={async (e) => {
          try {
            const updated = await api.updatePreferredModel(e.target.value);
            setSub(updated);
          } catch { /* ignore */ }
        }}
        title={t("subscription.preferredModel")}
        className="bg-transparent border border-neutral-800 text-[10px] font-mono text-neutral-400 px-1.5 py-0.5 outline-none cursor-pointer appearance-none hover:border-neutral-600 transition-colors"
      >
        {sub.allowed_models.map((m) => (
          <option key={m} value={m} className="bg-neutral-900 text-white">
            {m.split("/").pop()}
          </option>
        ))}
      </select>
    </div>
  );
}
