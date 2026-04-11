import { useState } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { CheckCircle2, XCircle, Loader2, Eye, EyeOff } from "lucide-react";

const API_BASE = import.meta.env.VITE_API_BASE ?? "";

export default function ResetPassword() {
  const { t } = useTranslation();
  const [params] = useSearchParams();
  const token = params.get("token");

  const [password, setPassword] = useState("");
  const [showPwd, setShowPwd] = useState(false);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<"form" | "success" | "error">("form");
  const [errorMsg, setErrorMsg] = useState("");

  if (!token) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="max-w-sm w-full border-2 border-neutral-800 p-8 text-center space-y-4">
          <XCircle size={32} className="mx-auto text-red-400" />
          <p className="font-mono text-sm text-red-400">
            {t("auth.invalidResetLink", "Invalid reset link")}
          </p>
        </div>
      </div>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg("");
    try {
      const res = await fetch(`${API_BASE}/api/auth/reset-password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, password }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || "Reset failed");
      }
      setStatus("success");
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : "Reset failed");
      setStatus("error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center h-full">
      <div className="max-w-sm w-full border-2 border-neutral-800 p-8 space-y-5">
        {status === "form" && (
          <>
            <h2 className="font-mono text-sm font-bold uppercase tracking-[0.15em] text-white text-center">
              {t("auth.resetPasswordTitle", "Reset Password")}
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-[10px] font-mono uppercase tracking-widest text-neutral-500 mb-1.5">
                  {t("auth.newPassword", "New Password")}
                </label>
                <div className="relative">
                  <input
                    type={showPwd ? "text" : "password"}
                    required
                    minLength={8}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full bg-transparent border border-neutral-700 focus:border-cyan-400 px-3 py-2 text-sm text-white font-mono outline-none placeholder-neutral-600 transition-colors pr-10"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPwd((v) => !v)}
                    className="absolute right-2 top-1/2 -translate-y-1/2 text-neutral-600 hover:text-neutral-400 transition-colors"
                    tabIndex={-1}
                  >
                    {showPwd ? <EyeOff size={14} /> : <Eye size={14} />}
                  </button>
                </div>
              </div>
              {errorMsg && <p className="text-[11px] font-mono text-red-400">{errorMsg}</p>}
              <button
                type="submit"
                disabled={loading}
                className="w-full py-2.5 border-2 border-cyan-400 text-cyan-400 font-mono text-xs uppercase tracking-wider font-bold hover:bg-cyan-400/10 transition-colors disabled:opacity-40 flex items-center justify-center gap-2"
              >
                {loading && <Loader2 size={14} className="animate-spin" />}
                {t("auth.resetPassword", "Reset Password")}
              </button>
            </form>
          </>
        )}
        {status === "success" && (
          <div className="text-center space-y-4">
            <CheckCircle2 size={32} className="mx-auto text-green-400" />
            <p className="font-mono text-sm text-white">
              {t("auth.passwordResetSuccess", "Password reset successfully!")}
            </p>
            <Link
              to="/"
              className="inline-block px-4 py-2 border border-cyan-400 text-cyan-400 font-mono text-xs uppercase tracking-wider hover:bg-cyan-400/10 transition-colors"
            >
              {t("auth.signIn")}
            </Link>
          </div>
        )}
        {status === "error" && errorMsg && (
          <div className="text-center space-y-4">
            <XCircle size={32} className="mx-auto text-red-400" />
            <p className="font-mono text-sm text-red-400">{errorMsg}</p>
            <button
              onClick={() => { setStatus("form"); setErrorMsg(""); }}
              className="inline-block px-4 py-2 border border-neutral-700 text-neutral-400 font-mono text-xs uppercase tracking-wider hover:text-white transition-colors"
            >
              {t("common.retry", "Try again")}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
