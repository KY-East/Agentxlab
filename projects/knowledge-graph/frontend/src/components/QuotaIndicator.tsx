import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Zap, X, ArrowUpRight } from "lucide-react";
import { useSubscription } from "../contexts/SubscriptionContext";
import PricingModal from "./PricingModal";

export default function QuotaIndicator() {
  const { t } = useTranslation();
  const { sub, showUpgradePrompt, setShowUpgradePrompt } = useSubscription();
  const [showPricing, setShowPricing] = useState(false);

  if (!sub) return null;

  const pct = (sub.tokens_used_this_month / sub.monthly_token_limit) * 100;
  const isLow = pct > 80;
  const isExhausted = pct >= 100;

  return (
    <>
      {/* Upgrade prompt banner - shown when API returns 429 */}
      {showUpgradePrompt && (
        <div className="fixed top-0 left-0 right-0 z-[90] flex items-center justify-center gap-3 px-4 py-2 bg-red-950/90 border-b border-red-800/60 backdrop-blur-sm">
          <Zap size={12} className="text-red-400 shrink-0" />
          <span className="font-mono text-[11px] text-red-300">
            {t("subscription.quotaExceeded")}
          </span>
          <button
            onClick={() => { setShowUpgradePrompt(false); setShowPricing(true); }}
            className="px-3 py-0.5 border border-cyan-400 text-cyan-400 font-mono text-[10px] uppercase tracking-wider hover:bg-cyan-400/10 transition-colors flex items-center gap-1"
          >
            <ArrowUpRight size={10} />
            {t("subscription.upgrade")}
          </button>
          <button
            onClick={() => setShowUpgradePrompt(false)}
            className="text-neutral-600 hover:text-white transition-colors ml-1"
          >
            <X size={12} />
          </button>
        </div>
      )}

      {/* Small token badge in header — only when running low */}
      {isLow && !showUpgradePrompt && (
        <button
          onClick={() => setShowPricing(true)}
          className={`flex items-center gap-1 px-2 py-0.5 border font-mono text-[10px] tabular-nums transition-colors ${
            isExhausted
              ? "border-red-800/50 text-red-400 hover:bg-red-900/20"
              : "border-yellow-800/50 text-yellow-500 hover:bg-yellow-900/20"
          }`}
          title={t("subscription.quotaWarning")}
        >
          <Zap size={9} />
          {Math.max(0, sub.monthly_token_limit - sub.tokens_used_this_month).toLocaleString()}
        </button>
      )}

      <PricingModal
        open={showPricing}
        onClose={() => setShowPricing(false)}
        currentPlan={sub.plan}
      />
    </>
  );
}
