import { useState } from "react";
import { useTranslation } from "react-i18next";
import { GoogleLogin } from "@react-oauth/google";
import { X, Loader2, Eye, EyeOff } from "lucide-react";

const API_BASE = import.meta.env.VITE_API_BASE ?? "";

type Tab = "login" | "register" | "forgot";

interface Props {
  open: boolean;
  onClose: () => void;
  onLoginSuccess: (token: string, user: unknown) => void;
  onGoogleLogin: (credential: string) => Promise<void>;
}

export default function AuthModal({ open, onClose, onLoginSuccess, onGoogleLogin }: Props) {
  const { t } = useTranslation();
  const [tab, setTab] = useState<Tab>("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [showPwd, setShowPwd] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  if (!open) return null;

  const reset = () => {
    setEmail("");
    setPassword("");
    setDisplayName("");
    setError(null);
    setSuccessMsg(null);
    setShowPwd(false);
  };

  const switchTab = (t: Tab) => {
    setTab(t);
    reset();
  };

  const handleRegister = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, display_name: displayName }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || `Registration failed (${res.status})`);
      }
      const data = await res.json();
      onLoginSuccess(data.token, data.user);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || `Login failed (${res.status})`);
      }
      const data = await res.json();
      onLoginSuccess(data.token, data.user);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  };

  const handleForgot = async () => {
    setLoading(true);
    setError(null);
    setSuccessMsg(null);
    try {
      const res = await fetch(`${API_BASE}/api/auth/forgot-password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
      if (!res.ok) throw new Error("Request failed");
      setSuccessMsg(t("auth.resetEmailSent"));
    } catch {
      setError(t("auth.resetFailed"));
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (tab === "login") handleLogin();
    else if (tab === "register") handleRegister();
    else handleForgot();
  };

  const inputClass =
    "w-full bg-transparent border border-neutral-700 focus:border-cyan-400 px-3 py-2 text-sm text-white font-mono outline-none placeholder-neutral-600 transition-colors";
  const labelClass =
    "block text-[10px] font-mono uppercase tracking-widest text-neutral-500 mb-1.5";

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center">
      <div className="absolute inset-0 bg-black/70" onClick={onClose} />
      <div className="relative w-full max-w-sm border-2 border-neutral-800 bg-[#0a0a0a] shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-3 border-b border-neutral-800">
          <h2 className="font-mono text-xs font-bold uppercase tracking-[0.15em] text-white">
            {tab === "login" && t("auth.signIn")}
            {tab === "register" && t("auth.createAccount")}
            {tab === "forgot" && t("auth.forgotPassword")}
          </h2>
          <button onClick={onClose} className="text-neutral-600 hover:text-white transition-colors">
            <X size={16} />
          </button>
        </div>

        {/* Body */}
        <form onSubmit={handleSubmit} className="px-5 py-5 space-y-4">
          {/* Google OAuth */}
          {tab !== "forgot" && (
            <div className="flex justify-center pb-3 border-b border-neutral-800">
              <GoogleLogin
                onSuccess={(resp) => {
                  if (resp.credential) {
                    setError(null);
                    onGoogleLogin(resp.credential)
                      .then(() => onClose())
                      .catch((err) => {
                        setError(err instanceof Error ? err.message : t("auth.googleFailed", "Google login failed"));
                      });
                  }
                }}
                onError={() => {
                  setError(t("auth.googleFailed", "Google login failed"));
                }}
                size="medium"
                shape="rectangular"
                theme="filled_black"
                text={tab === "login" ? "signin_with" : "signup_with"}
                width="300"
              />
            </div>
          )}

          {tab !== "forgot" && (
            <div className="text-center">
              <span className="text-[10px] font-mono uppercase tracking-wider text-neutral-600">
                {t("auth.orWithEmail")}
              </span>
            </div>
          )}

          {/* Email */}
          <div>
            <label className={labelClass}>{t("auth.email")}</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              className={inputClass}
              autoComplete="email"
            />
          </div>

          {/* Password (not for forgot) */}
          {tab !== "forgot" && (
            <div>
              <label className={labelClass}>{t("auth.password")}</label>
              <div className="relative">
                <input
                  type={showPwd ? "text" : "password"}
                  required
                  minLength={8}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className={`${inputClass} pr-10`}
                  autoComplete={tab === "login" ? "current-password" : "new-password"}
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
          )}

          {/* Display name (register only) */}
          {tab === "register" && (
            <div>
              <label className={labelClass}>{t("auth.displayName")}</label>
              <input
                type="text"
                required
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                placeholder="Researcher X"
                className={inputClass}
                autoComplete="name"
              />
            </div>
          )}

          {/* Error / Success */}
          {error && (
            <p className="text-[11px] font-mono text-red-400">{error}</p>
          )}
          {successMsg && (
            <p className="text-[11px] font-mono text-cyan-400">{successMsg}</p>
          )}

          {/* Submit */}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 border-2 border-cyan-400 text-cyan-400 font-mono text-xs uppercase tracking-wider font-bold hover:bg-cyan-400/10 transition-colors disabled:opacity-40 flex items-center justify-center gap-2"
          >
            {loading && <Loader2 size={14} className="animate-spin" />}
            {tab === "login" && t("auth.signIn")}
            {tab === "register" && t("auth.createAccount")}
            {tab === "forgot" && t("auth.sendResetLink")}
          </button>
        </form>

        {/* Footer links */}
        <div className="px-5 pb-4 space-y-2">
          {tab === "login" && (
            <>
              <button
                onClick={() => switchTab("forgot")}
                className="block w-full text-center text-[10px] font-mono text-neutral-600 hover:text-cyan-400 transition-colors uppercase tracking-wider"
              >
                {t("auth.forgotPassword")}
              </button>
              <p className="text-center text-[10px] font-mono text-neutral-600">
                {t("auth.noAccount")}{" "}
                <button
                  onClick={() => switchTab("register")}
                  className="text-cyan-400 hover:text-white transition-colors uppercase tracking-wider"
                >
                  {t("auth.createAccount")}
                </button>
              </p>
            </>
          )}
          {tab === "register" && (
            <p className="text-center text-[10px] font-mono text-neutral-600">
              {t("auth.hasAccount")}{" "}
              <button
                onClick={() => switchTab("login")}
                className="text-cyan-400 hover:text-white transition-colors uppercase tracking-wider"
              >
                {t("auth.signIn")}
              </button>
            </p>
          )}
          {tab === "forgot" && (
            <button
              onClick={() => switchTab("login")}
              className="block w-full text-center text-[10px] font-mono text-neutral-600 hover:text-cyan-400 transition-colors uppercase tracking-wider"
            >
              {t("auth.backToLogin")}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
