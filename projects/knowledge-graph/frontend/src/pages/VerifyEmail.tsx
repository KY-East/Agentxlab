import { useEffect, useState } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { CheckCircle2, XCircle, Loader2 } from "lucide-react";
import { useAuth } from "../contexts/AuthContext";

const API_BASE = import.meta.env.VITE_API_BASE ?? "";

export default function VerifyEmail() {
  const { t } = useTranslation();
  const { refreshUser } = useAuth();
  const [params] = useSearchParams();
  const token = params.get("token");
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");

  useEffect(() => {
    if (!token) {
      setStatus("error");
      return;
    }
    fetch(`${API_BASE}/api/auth/verify-email?token=${encodeURIComponent(token)}`)
      .then(async (r) => {
        if (r.ok) {
          setStatus("success");
          await refreshUser();
        } else {
          setStatus("error");
        }
      })
      .catch(() => setStatus("error"));
  }, [token, refreshUser]);

  return (
    <div className="flex items-center justify-center h-full">
      <div className="max-w-sm w-full border-2 border-neutral-800 p-8 text-center space-y-4">
        {status === "loading" && (
          <>
            <Loader2 size={32} className="mx-auto animate-spin text-cyan-400" />
            <p className="font-mono text-xs text-neutral-400 uppercase tracking-wider">
              {t("common.loading")}
            </p>
          </>
        )}
        {status === "success" && (
          <>
            <CheckCircle2 size={32} className="mx-auto text-green-400" />
            <p className="font-mono text-sm text-white">
              {t("auth.emailVerifiedSuccess", "Email verified successfully!")}
            </p>
            <Link
              to="/"
              className="inline-block mt-4 px-4 py-2 border border-cyan-400 text-cyan-400 font-mono text-xs uppercase tracking-wider hover:bg-cyan-400/10 transition-colors"
            >
              {t("common.backHome", "Back to home")}
            </Link>
          </>
        )}
        {status === "error" && (
          <>
            <XCircle size={32} className="mx-auto text-red-400" />
            <p className="font-mono text-sm text-red-400">
              {t("auth.verifyFailed", "Invalid or expired verification link")}
            </p>
            <Link
              to="/"
              className="inline-block mt-4 px-4 py-2 border border-neutral-700 text-neutral-400 font-mono text-xs uppercase tracking-wider hover:text-white transition-colors"
            >
              {t("common.backHome", "Back to home")}
            </Link>
          </>
        )}
      </div>
    </div>
  );
}
