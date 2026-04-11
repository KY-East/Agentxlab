import { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { X, Loader2, Check, Copy, ExternalLink } from "lucide-react";
import { api } from "../api/client";
import type { PlanInfo } from "../types";

interface Props {
  open: boolean;
  onClose: () => void;
  currentPlan?: string;
}

export default function PricingModal({ open, onClose, currentPlan = "free" }: Props) {
  const { t, i18n } = useTranslation();
  const isZh = i18n.language?.startsWith("zh");

  const [plans, setPlans] = useState<PlanInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionPlan, setActionPlan] = useState<string | null>(null);
  const [cryptoInfo, setCryptoInfo] = useState<{
    wallet_address: string;
    network: string;
    amount_usd: number;
    memo: string;
    payment_id: number;
  } | null>(null);
  const [txHash, setTxHash] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [copied, setCopied] = useState(false);
  const [submitMsg, setSubmitMsg] = useState<string | null>(null);

  useEffect(() => {
    if (!open) return;
    setLoading(true);
    api.getPlans().then(setPlans).catch(() => {}).finally(() => setLoading(false));
  }, [open]);

  if (!open) return null;

  const handleStripeCheckout = async (plan: string) => {
    setActionPlan(plan);
    try {
      const res = await api.createStripeCheckout(plan);
      window.location.href = res.checkout_url;
    } catch {
      setActionPlan(null);
    }
  };

  const handleCryptoRequest = async (plan: string) => {
    setActionPlan(plan);
    try {
      const res = await api.requestCryptoPayment(plan);
      setCryptoInfo(res);
    } catch {
      setActionPlan(null);
    }
  };

  const handleSubmitTx = async () => {
    if (!cryptoInfo || !txHash.trim()) return;
    setSubmitting(true);
    setSubmitMsg(null);
    try {
      await api.submitCryptoTx(cryptoInfo.payment_id, txHash.trim());
      setSubmitMsg(t("pricing.txSubmitted"));
    } catch {
      setSubmitMsg(t("pricing.txFailed"));
    } finally {
      setSubmitting(false);
    }
  };

  const copyAddr = () => {
    if (!cryptoInfo) return;
    navigator.clipboard.writeText(cryptoInfo.wallet_address);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const formatTokens = (n: number) => {
    if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
    if (n >= 1_000) return `${(n / 1_000).toFixed(0)}K`;
    return String(n);
  };

  const planOrder = ["free", "pro", "lifetime"];
  const sorted = [...plans].sort((a, b) => planOrder.indexOf(a.name) - planOrder.indexOf(b.name));

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center">
      <div className="absolute inset-0 bg-black/70" onClick={onClose} />
      <div className="relative w-full max-w-3xl border-2 border-neutral-800 bg-[#0a0a0a] shadow-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between px-6 py-3 border-b border-neutral-800 sticky top-0 bg-[#0a0a0a] z-10">
          <h2 className="font-mono text-xs font-bold uppercase tracking-[0.15em] text-white">
            {t("pricing.title")}
          </h2>
          <button onClick={onClose} className="text-neutral-600 hover:text-white transition-colors">
            <X size={16} />
          </button>
        </div>

        {loading ? (
          <div className="flex justify-center py-16">
            <Loader2 size={20} className="animate-spin text-neutral-600" />
          </div>
        ) : cryptoInfo ? (
          <div className="px-6 py-6 space-y-4">
            <h3 className="font-mono text-sm font-bold text-white uppercase tracking-wider">
              {t("pricing.cryptoPayment")}
            </h3>
            <div className="border border-neutral-800 p-4 space-y-3">
              <div>
                <span className="text-[10px] font-mono uppercase tracking-wider text-neutral-500 block mb-1">
                  {t("pricing.network")}
                </span>
                <span className="font-mono text-sm text-white">{cryptoInfo.network}</span>
              </div>
              <div>
                <span className="text-[10px] font-mono uppercase tracking-wider text-neutral-500 block mb-1">
                  {t("pricing.amount")}
                </span>
                <span className="font-mono text-lg font-bold text-cyan-400">
                  ${cryptoInfo.amount_usd} USDT
                </span>
              </div>
              <div>
                <span className="text-[10px] font-mono uppercase tracking-wider text-neutral-500 block mb-1">
                  {t("pricing.walletAddress")}
                </span>
                <div className="flex items-center gap-2">
                  <code className="font-mono text-xs text-white bg-neutral-900 px-2 py-1 border border-neutral-800 break-all flex-1">
                    {cryptoInfo.wallet_address}
                  </code>
                  <button onClick={copyAddr} className="text-neutral-500 hover:text-cyan-400 transition-colors shrink-0">
                    {copied ? <Check size={14} /> : <Copy size={14} />}
                  </button>
                </div>
              </div>
              <div>
                <span className="text-[10px] font-mono uppercase tracking-wider text-neutral-500 block mb-1">
                  {t("pricing.memo")}
                </span>
                <code className="font-mono text-xs text-yellow-500 bg-neutral-900 px-2 py-1 border border-neutral-800">
                  {cryptoInfo.memo}
                </code>
              </div>
              <div className="border-t border-neutral-800 pt-3">
                <span className="text-[10px] font-mono uppercase tracking-wider text-neutral-500 block mb-1.5">
                  {t("pricing.txHashLabel")}
                </span>
                <input
                  value={txHash}
                  onChange={(e) => setTxHash(e.target.value)}
                  placeholder="0x..."
                  className="w-full bg-transparent border border-neutral-700 focus:border-cyan-400 px-3 py-2 text-sm text-white font-mono outline-none placeholder-neutral-600"
                />
                <div className="flex items-center gap-3 mt-2">
                  <button
                    onClick={handleSubmitTx}
                    disabled={!txHash.trim() || submitting}
                    className="px-4 py-2 border border-cyan-400 text-cyan-400 font-mono text-[11px] uppercase tracking-wider hover:bg-cyan-400/10 transition-colors disabled:opacity-40"
                  >
                    {submitting ? <Loader2 size={12} className="animate-spin" /> : t("pricing.submitTx")}
                  </button>
                  <button
                    onClick={() => { setCryptoInfo(null); setActionPlan(null); setTxHash(""); setSubmitMsg(null); }}
                    className="px-4 py-2 border border-neutral-700 text-neutral-500 font-mono text-[11px] uppercase tracking-wider hover:text-white transition-colors"
                  >
                    {t("pricing.back")}
                  </button>
                </div>
                {submitMsg && (
                  <p className={`mt-2 text-[11px] font-mono ${submitMsg.includes("fail") || submitMsg.includes("失败") ? "text-red-400" : "text-cyan-400"}`}>
                    {submitMsg}
                  </p>
                )}
              </div>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-0 md:gap-px bg-neutral-800/50">
            {sorted.map((plan) => {
              const isCurrent = plan.name === currentPlan;
              const label = isZh ? plan.label_zh : plan.label_en;
              const price = plan.price_monthly_cents > 0
                ? `$${(plan.price_monthly_cents / 100).toFixed(2)}/mo`
                : plan.price_once_cents > 0
                  ? `$${(plan.price_once_cents / 100).toFixed(0)} ${t("pricing.once")}`
                  : t("pricing.free");

              return (
                <div
                  key={plan.name}
                  className={`bg-[#0a0a0a] p-5 flex flex-col ${
                    plan.name === "pro" ? "border-x border-cyan-800/30" : ""
                  }`}
                >
                  <div className="mb-4">
                    <h3 className="font-mono text-sm font-bold uppercase tracking-wider text-white">
                      {label}
                    </h3>
                    <p className="font-mono text-2xl font-bold text-cyan-400 mt-2">{price}</p>
                  </div>

                  <div className="space-y-2 flex-1 mb-5">
                    <div className="flex items-start gap-2">
                      <Check size={12} className="text-cyan-400 mt-0.5 shrink-0" />
                      <span className="font-mono text-[11px] text-neutral-400">
                        {formatTokens(plan.monthly_tokens)} tokens / {t("pricing.month")}
                      </span>
                    </div>
                    {plan.allowed_models.map((m) => (
                      <div key={m} className="flex items-start gap-2">
                        <Check size={12} className="text-cyan-400 mt-0.5 shrink-0" />
                        <span className="font-mono text-[11px] text-neutral-400">
                          {m.split("/").pop()}
                        </span>
                      </div>
                    ))}
                    {plan.name === "lifetime" && (
                      <div className="flex items-start gap-2">
                        <Check size={12} className="text-cyan-400 mt-0.5 shrink-0" />
                        <span className="font-mono text-[11px] text-neutral-400">
                          {t("pricing.lifetimeAccess")}
                        </span>
                      </div>
                    )}
                  </div>

                  {isCurrent ? (
                    <div className="py-2.5 border border-neutral-700 text-center font-mono text-[11px] uppercase tracking-wider text-neutral-500">
                      {t("pricing.currentPlan")}
                    </div>
                  ) : plan.name === "free" ? (
                    <div className="py-2.5 border border-neutral-800 text-center font-mono text-[11px] uppercase tracking-wider text-neutral-700">
                      {t("pricing.default")}
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <button
                        onClick={() => handleStripeCheckout(plan.name)}
                        disabled={actionPlan === plan.name}
                        className="w-full py-2.5 border-2 border-cyan-400 text-cyan-400 font-mono text-[11px] uppercase tracking-wider font-bold hover:bg-cyan-400/10 transition-colors disabled:opacity-40 flex items-center justify-center gap-2"
                      >
                        {actionPlan === plan.name ? (
                          <Loader2 size={12} className="animate-spin" />
                        ) : (
                          <ExternalLink size={12} />
                        )}
                        {plan.name === "pro" ? t("pricing.subscribe") : t("pricing.buyOnce")}
                      </button>
                      <button
                        onClick={() => handleCryptoRequest(plan.name)}
                        className="w-full py-2 border border-yellow-600/50 text-yellow-500 font-mono text-[10px] uppercase tracking-wider hover:bg-yellow-900/10 transition-colors"
                      >
                        {t("pricing.payWithCrypto")}
                      </button>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
