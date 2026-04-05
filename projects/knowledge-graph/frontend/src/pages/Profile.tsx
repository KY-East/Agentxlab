import { useAuth } from "../contexts/AuthContext";
import { useNavigate } from "react-router-dom";
import { useEffect } from "react";
import { useTranslation } from "react-i18next";
import { User, Award, FileText } from "lucide-react";

export default function Profile() {
  const { t, i18n } = useTranslation();
  const { user, loading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!loading && !user) navigate("/");
  }, [loading, user, navigate]);

  if (loading || !user) {
    return <div className="p-8 text-gray-400">{t("common.loading")}</div>;
  }

  return (
    <div className="h-full overflow-y-auto p-8">
      <div className="max-w-2xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          {user.avatar_url ? (
            <img src={user.avatar_url} alt="" className="w-16 h-16 rounded-full" />
          ) : (
            <div className="w-16 h-16 rounded-full bg-violet-600 flex items-center justify-center text-2xl font-bold">
              {user.display_name.charAt(0).toUpperCase()}
            </div>
          )}
          <div>
            <h1 className="text-xl font-bold">{user.display_name}</h1>
            <p className="text-sm text-gray-400">{user.email}</p>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-gray-900 border border-white/10 rounded-xl p-4 text-center">
            <Award size={20} className="mx-auto mb-1 text-yellow-400" />
            <p className="text-2xl font-bold text-violet-300">
              {user.points.toLocaleString(i18n.language === "zh" ? "zh-CN" : "en-US")}
            </p>
            <p className="text-xs text-gray-500">{t("profile.points")}</p>
          </div>
          <div className="bg-gray-900 border border-white/10 rounded-xl p-4 text-center">
            <FileText size={20} className="mx-auto mb-1 text-blue-400" />
            <p className="text-2xl font-bold text-blue-300">—</p>
            <p className="text-xs text-gray-500">{t("profile.posts")}</p>
          </div>
          <div className="bg-gray-900 border border-white/10 rounded-xl p-4 text-center">
            <User size={20} className="mx-auto mb-1 text-green-400" />
            <p className="text-2xl font-bold text-green-300 capitalize">{user.role}</p>
            <p className="text-xs text-gray-500">{t("profile.role")}</p>
          </div>
        </div>

        {/* Placeholder sections */}
        <section className="bg-gray-900 border border-white/10 rounded-xl p-6">
          <h2 className="text-lg font-semibold mb-3">{t("profile.myPosts")}</h2>
          <p className="text-sm text-gray-500">{t("profile.postsComingSoon")}</p>
        </section>

        <section className="bg-gray-900 border border-white/10 rounded-xl p-6">
          <h2 className="text-lg font-semibold mb-3">{t("profile.pointHistory")}</h2>
          <p className="text-sm text-gray-500">{t("profile.pointHistoryComingSoon")}</p>
        </section>

        {user.did_address && (
          <section className="bg-gray-900 border border-white/10 rounded-xl p-6">
            <h2 className="text-lg font-semibold mb-3">{t("profile.web3Identity")}</h2>
            <p className="text-sm text-gray-400 font-mono break-all">{user.did_address}</p>
          </section>
        )}
      </div>
    </div>
  );
}
