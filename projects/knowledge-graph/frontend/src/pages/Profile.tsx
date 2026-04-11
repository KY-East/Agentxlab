import { useAuth } from "../contexts/AuthContext";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useState, useEffect, useCallback } from "react";
import { useTranslation } from "react-i18next";
import {
  Award,
  FileText,
  Clock,
  Save,
  Pencil,
  X,
  ChevronRight,
  Loader2,
  Swords,
  Zap,
  CreditCard,
  ArrowUpRight,
} from "lucide-react";
import { api } from "../api/client";
import type { ForumPost, PointLogEntry, DebateBrief, SubscriptionInfo } from "../types";
import PricingModal from "../components/PricingModal";

export default function Profile() {
  const { t } = useTranslation();
  const { user, loading: authLoading, refreshUser } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const [editing, setEditing] = useState(false);
  const [editName, setEditName] = useState("");
  const [editAvatar, setEditAvatar] = useState("");
  const [saving, setSaving] = useState(false);
  const [saveMsg, setSaveMsg] = useState<string | null>(null);

  const [posts, setPosts] = useState<ForumPost[]>([]);
  const [postsLoading, setPostsLoading] = useState(false);

  const [pointLog, setPointLog] = useState<PointLogEntry[]>([]);
  const [pointsLoading, setPointsLoading] = useState(false);

  const [debates, setDebates] = useState<DebateBrief[]>([]);
  const [debatesLoading, setDebatesLoading] = useState(false);

  const [sub, setSub] = useState<SubscriptionInfo | null>(null);
  const [subLoading, setSubLoading] = useState(false);
  const [showPricing, setShowPricing] = useState(false);
  const [portalLoading, setPortalLoading] = useState(false);

  const [activeTab, setActiveTab] = useState<"posts" | "debates" | "points">("posts");

  useEffect(() => {
    if (searchParams.get("payment") === "success") {
      setSaveMsg(t("subscription.active"));
      setTimeout(() => setSaveMsg(null), 4000);
    }
  }, [searchParams, t]);

  useEffect(() => {
    if (!authLoading && !user) navigate("/");
  }, [authLoading, user, navigate]);

  const loadPosts = useCallback(async () => {
    if (!user) return;
    setPostsLoading(true);
    try {
      const res = await api.listForumPosts({ user_id: user.id, sort: "newest", limit: 50 });
      setPosts(res);
    } catch {
      setPosts([]);
    } finally {
      setPostsLoading(false);
    }
  }, [user]);

  const loadDebates = useCallback(async () => {
    if (!user) return;
    setDebatesLoading(true);
    try {
      const res = await api.getDebates({ created_by: user.id });
      setDebates(res);
    } catch {
      setDebates([]);
    } finally {
      setDebatesLoading(false);
    }
  }, [user]);

  const loadPoints = useCallback(async () => {
    setPointsLoading(true);
    try {
      const res = await api.getPointLog(50);
      setPointLog(res);
    } catch {
      setPointLog([]);
    } finally {
      setPointsLoading(false);
    }
  }, []);

  const loadSub = useCallback(async () => {
    setSubLoading(true);
    try {
      const res = await api.getMySubscription();
      setSub(res);
    } catch {
      setSub(null);
    } finally {
      setSubLoading(false);
    }
  }, []);

  useEffect(() => {
    if (user) {
      loadPosts();
      loadDebates();
      loadPoints();
      loadSub();
    }
  }, [user, loadPosts, loadDebates, loadPoints, loadSub]);

  const handleEdit = () => {
    if (!user) return;
    setEditName(user.display_name);
    setEditAvatar(user.avatar_url ?? "");
    setEditing(true);
    setSaveMsg(null);
  };

  const handleSave = async () => {
    setSaving(true);
    setSaveMsg(null);
    try {
      await api.updateMe({
        display_name: editName.trim() || undefined,
        avatar_url: editAvatar.trim() || undefined,
      });
      await refreshUser();
      setEditing(false);
      setSaveMsg(t("profile.saved"));
      setTimeout(() => setSaveMsg(null), 2000);
    } catch {
      setSaveMsg(t("profile.saveFailed"));
    } finally {
      setSaving(false);
    }
  };

  if (authLoading || !user) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 size={16} className="animate-spin text-neutral-600" />
      </div>
    );
  }

  const tabs = [
    { key: "posts" as const, label: t("profile.myPosts"), count: posts.length },
    { key: "debates" as const, label: t("profile.myDebates"), count: debates.length },
    { key: "points" as const, label: t("profile.pointHistory"), count: pointLog.length },
  ];

  return (
    <div className="h-full overflow-y-auto bg-neutral-950">
      <div className="max-w-3xl mx-auto px-4 py-8 space-y-6">

        {/* User Card */}
        <div className="border border-neutral-800 p-6">
          <div className="flex items-start gap-5">
            {user.avatar_url ? (
              <img
                src={user.avatar_url}
                alt=""
                className="w-16 h-16 border border-neutral-700 object-cover shrink-0"
              />
            ) : (
              <div className="w-16 h-16 border border-neutral-700 bg-neutral-900 flex items-center justify-center text-2xl font-bold text-cyan-400 font-mono shrink-0">
                {user.display_name.charAt(0).toUpperCase()}
              </div>
            )}

            <div className="flex-1 min-w-0">
              {editing ? (
                <div className="space-y-3">
                  <div>
                    <label className="block text-[10px] font-mono uppercase tracking-widest text-neutral-600 mb-1">
                      {t("profile.displayName")}
                    </label>
                    <input
                      value={editName}
                      onChange={(e) => setEditName(e.target.value)}
                      className="w-full bg-transparent border border-neutral-700 focus:border-cyan-400 px-3 py-1.5 text-sm text-white font-mono outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] font-mono uppercase tracking-widest text-neutral-600 mb-1">
                      {t("profile.avatarUrl")}
                    </label>
                    <input
                      value={editAvatar}
                      onChange={(e) => setEditAvatar(e.target.value)}
                      placeholder="https://..."
                      className="w-full bg-transparent border border-neutral-700 focus:border-cyan-400 px-3 py-1.5 text-sm text-white font-mono outline-none placeholder-neutral-700"
                    />
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={handleSave}
                      disabled={saving}
                      className="flex items-center gap-1.5 px-3 py-1 border border-cyan-400 text-cyan-400 text-[11px] font-mono uppercase tracking-wider hover:bg-cyan-400/10 transition-colors disabled:opacity-40"
                    >
                      <Save size={12} />
                      {saving ? t("profile.saving") : t("profile.save")}
                    </button>
                    <button
                      onClick={() => setEditing(false)}
                      className="px-3 py-1 border border-neutral-700 text-neutral-500 text-[11px] font-mono uppercase tracking-wider hover:text-white transition-colors"
                    >
                      <X size={12} />
                    </button>
                  </div>
                </div>
              ) : (
                <>
                  <h1 className="text-lg font-bold text-white font-mono truncate">
                    {user.display_name}
                  </h1>
                  <p className="text-[11px] text-neutral-600 font-mono">{user.email}</p>
                  <div className="flex items-center gap-4 mt-3">
                    <span className="text-[11px] font-mono uppercase tracking-wider text-neutral-500">
                      {user.role}
                    </span>
                    {user.did_address && (
                      <span className="text-[10px] font-mono text-neutral-700 truncate max-w-[200px]">
                        {user.did_address}
                      </span>
                    )}
                  </div>
                  <button
                    onClick={handleEdit}
                    className="mt-3 flex items-center gap-1.5 text-[10px] font-mono uppercase tracking-wider text-neutral-600 hover:text-cyan-400 transition-colors"
                  >
                    <Pencil size={10} />
                    {t("profile.editProfile")}
                  </button>
                </>
              )}
              {saveMsg && (
                <p className={`mt-2 text-[10px] font-mono ${saveMsg.includes("fail") || saveMsg.includes("失败") ? "text-red-400" : "text-cyan-400"}`}>
                  {saveMsg}
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Stats Row */}
        <div className="grid grid-cols-4 gap-3">
          <div className="border border-neutral-800 p-4 text-center">
            <Award size={16} className="mx-auto mb-1.5 text-cyan-400" />
            <p className="text-xl font-bold text-white font-mono tabular-nums">
              {user.points.toLocaleString()}
            </p>
            <p className="text-[10px] font-mono uppercase tracking-widest text-neutral-600">
              {t("profile.points")}
            </p>
          </div>
          <div className="border border-neutral-800 p-4 text-center">
            <FileText size={16} className="mx-auto mb-1.5 text-neutral-500" />
            <p className="text-xl font-bold text-white font-mono tabular-nums">
              {posts.length}
            </p>
            <p className="text-[10px] font-mono uppercase tracking-widest text-neutral-600">
              {t("profile.posts")}
            </p>
          </div>
          <div className="border border-neutral-800 p-4 text-center">
            <Swords size={16} className="mx-auto mb-1.5 text-neutral-500" />
            <p className="text-xl font-bold text-white font-mono tabular-nums">
              {debates.length}
            </p>
            <p className="text-[10px] font-mono uppercase tracking-widest text-neutral-600">
              {t("profile.myDebates")}
            </p>
          </div>
          <div className="border border-neutral-800 p-4 text-center">
            <Clock size={16} className="mx-auto mb-1.5 text-neutral-500" />
            <p className="text-xl font-bold text-white font-mono tabular-nums">
              {pointLog.length}
            </p>
            <p className="text-[10px] font-mono uppercase tracking-widest text-neutral-600">
              {t("profile.pointHistory")}
            </p>
          </div>
        </div>

        {/* Subscription Card */}
        <div className="border border-neutral-800 p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-[11px] font-mono font-bold uppercase tracking-[0.15em] text-white flex items-center gap-2">
              <CreditCard size={14} className="text-cyan-400" />
              {t("subscription.title")}
            </h2>
            {sub && sub.plan !== "free" && sub.stripe_customer_id && (
              <button
                onClick={async () => {
                  setPortalLoading(true);
                  try {
                    const res = await api.createStripePortal();
                    window.location.href = res.portal_url;
                  } catch {
                    setPortalLoading(false);
                  }
                }}
                disabled={portalLoading}
                className="text-[10px] font-mono uppercase tracking-wider text-neutral-500 hover:text-cyan-400 transition-colors flex items-center gap-1"
              >
                <ArrowUpRight size={10} />
                {t("subscription.manage")}
              </button>
            )}
          </div>

          {subLoading ? (
            <div className="flex justify-center py-4">
              <Loader2 size={14} className="animate-spin text-neutral-600" />
            </div>
          ) : sub ? (
            <div className="space-y-3">
              <div className="flex items-center gap-4">
                <div>
                  <span className="text-[10px] font-mono uppercase tracking-wider text-neutral-600 block">
                    {t("subscription.plan")}
                  </span>
                  <span className="text-sm font-mono font-bold text-white uppercase">
                    {sub.plan}
                  </span>
                </div>
                <div>
                  <span className="text-[10px] font-mono uppercase tracking-wider text-neutral-600 block">
                    {t("subscription.status")}
                  </span>
                  <span className={`text-sm font-mono font-bold uppercase ${
                    sub.status === "active" ? "text-green-500" : sub.status === "pending_crypto" ? "text-yellow-500" : "text-red-400"
                  }`}>
                    {t(`subscription.${sub.status}`, sub.status)}
                  </span>
                </div>
                {sub.preferred_model && (
                  <div>
                    <span className="text-[10px] font-mono uppercase tracking-wider text-neutral-600 block">
                      {t("subscription.preferredModel")}
                    </span>
                    <span className="text-sm font-mono text-neutral-300">
                      {sub.preferred_model.split("/").pop()}
                    </span>
                  </div>
                )}
              </div>

              {/* Token Usage Bar */}
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[10px] font-mono uppercase tracking-wider text-neutral-600 flex items-center gap-1.5">
                    <Zap size={10} className="text-cyan-400" />
                    {t("subscription.tokenUsage")}
                  </span>
                  <span className="text-[10px] font-mono tabular-nums text-neutral-500">
                    {sub.tokens_used_this_month.toLocaleString()} / {sub.monthly_token_limit.toLocaleString()}
                  </span>
                </div>
                <div className="h-2 bg-neutral-900 border border-neutral-800 overflow-hidden">
                  {(() => {
                    const pct = Math.min(100, (sub.tokens_used_this_month / sub.monthly_token_limit) * 100);
                    const color = pct > 90 ? "bg-red-500" : pct > 70 ? "bg-yellow-500" : "bg-cyan-400";
                    return <div className={`h-full ${color} transition-all`} style={{ width: `${pct}%` }} />;
                  })()}
                </div>
                {sub.quota_reset_at && (
                  <p className="text-[10px] font-mono text-neutral-700 mt-1">
                    {t("subscription.resetAt")}: {new Date(sub.quota_reset_at).toLocaleDateString()}
                  </p>
                )}
              </div>

              {/* Upgrade Button */}
              {sub.plan === "free" && (
                <button
                  onClick={() => setShowPricing(true)}
                  className="w-full py-2 border-2 border-cyan-400 text-cyan-400 font-mono text-[11px] uppercase tracking-wider font-bold hover:bg-cyan-400/10 transition-colors"
                >
                  {t("subscription.upgrade")}
                </button>
              )}
            </div>
          ) : (
            <button
              onClick={() => setShowPricing(true)}
              className="w-full py-2 border border-neutral-700 text-neutral-400 font-mono text-[11px] uppercase tracking-wider hover:text-cyan-400 hover:border-cyan-400 transition-colors"
            >
              {t("subscription.upgrade")}
            </button>
          )}
        </div>

        {/* Model Selector */}
        {sub && sub.allowed_models.length > 1 && (
          <div className="border border-neutral-800 p-4">
            <label className="text-[10px] font-mono uppercase tracking-wider text-neutral-600 block mb-1.5">
              {t("subscription.preferredModel")}
            </label>
            <select
              value={sub.preferred_model || ""}
              onChange={async (e) => {
                try {
                  const updated = await api.updatePreferredModel(e.target.value);
                  setSub(updated);
                } catch { /* ignore */ }
              }}
              className="w-full bg-transparent border border-neutral-700 focus:border-cyan-400 px-3 py-2 text-sm text-white font-mono outline-none appearance-none cursor-pointer"
            >
              {sub.allowed_models.map((m) => (
                <option key={m} value={m} className="bg-neutral-900">
                  {m}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Tab Bar */}
        <div className="flex border-b border-neutral-800">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`px-4 py-2 text-[11px] font-mono uppercase tracking-wider transition-colors border-b-2 ${
                activeTab === tab.key
                  ? "border-cyan-400 text-cyan-400"
                  : "border-transparent text-neutral-600 hover:text-white"
              }`}
            >
              {tab.label} ({tab.count})
            </button>
          ))}
        </div>

        {/* Tab Content */}
        {activeTab === "posts" && (
          <div className="space-y-1">
            {postsLoading ? (
              <div className="flex justify-center py-8">
                <Loader2 size={14} className="animate-spin text-neutral-600" />
              </div>
            ) : posts.length === 0 ? (
              <p className="text-center text-neutral-600 text-[11px] font-mono py-8">
                {t("profile.noPosts")}
              </p>
            ) : (
              posts.map((post) => (
                <button
                  key={post.id}
                  onClick={() => navigate(`/forum/${post.id}`)}
                  className="w-full text-left flex items-center gap-3 px-3 py-2.5 border border-neutral-800 hover:border-neutral-700 transition-colors group"
                >
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-white font-mono truncate group-hover:text-cyan-400 transition-colors">
                      {post.title}
                    </p>
                    <div className="flex items-center gap-3 mt-1">
                      <span className="text-[10px] font-mono text-neutral-600">
                        {t(`forum.postStatus.${post.status}`, post.status)}
                      </span>
                      <span className="text-[10px] font-mono text-neutral-700 tabular-nums">
                        {new Date(post.created_at).toLocaleDateString()}
                      </span>
                      <span className="text-[10px] font-mono text-neutral-700 tabular-nums">
                        {post.vote_score} pts
                      </span>
                    </div>
                  </div>
                  <ChevronRight size={12} className="text-neutral-700 group-hover:text-cyan-400 transition-colors shrink-0" />
                </button>
              ))
            )}
          </div>
        )}

        {activeTab === "debates" && (
          <div className="space-y-1">
            {debatesLoading ? (
              <div className="flex justify-center py-8">
                <Loader2 size={14} className="animate-spin text-neutral-600" />
              </div>
            ) : debates.length === 0 ? (
              <p className="text-center text-neutral-600 text-[11px] font-mono py-8">
                {t("profile.noDebates")}
              </p>
            ) : (
              debates.map((d) => (
                <button
                  key={d.id}
                  onClick={() => navigate(`/debate/${d.id}`)}
                  className="w-full text-left flex items-center gap-3 px-3 py-2.5 border border-neutral-800 hover:border-neutral-700 transition-colors group"
                >
                  <Swords size={14} className="text-neutral-600 shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-white font-mono truncate group-hover:text-cyan-400 transition-colors">
                      {d.title}
                    </p>
                    <div className="flex items-center gap-3 mt-1">
                      <span className={`text-[10px] font-mono uppercase tracking-wider ${
                        d.status === "completed" ? "text-green-500" : d.status === "active" ? "text-cyan-400" : "text-yellow-500"
                      }`}>
                        {d.status}
                      </span>
                      <span className="text-[10px] font-mono text-neutral-600">
                        {d.mode}
                      </span>
                      <span className="text-[10px] font-mono text-neutral-700 tabular-nums">
                        {new Date(d.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                  <ChevronRight size={12} className="text-neutral-700 group-hover:text-cyan-400 transition-colors shrink-0" />
                </button>
              ))
            )}
          </div>
        )}

        {activeTab === "points" && (
          <div className="space-y-1">
            {pointsLoading ? (
              <div className="flex justify-center py-8">
                <Loader2 size={14} className="animate-spin text-neutral-600" />
              </div>
            ) : pointLog.length === 0 ? (
              <p className="text-center text-neutral-600 text-[11px] font-mono py-8">
                {t("profile.noPointHistory")}
              </p>
            ) : (
              pointLog.map((entry) => (
                <div
                  key={entry.id}
                  className="flex items-center justify-between px-3 py-2.5 border border-neutral-800"
                >
                  <div className="flex items-center gap-3">
                    <span className={`text-sm font-mono font-bold tabular-nums ${entry.points > 0 ? "text-cyan-400" : "text-red-400"}`}>
                      {entry.points > 0 ? "+" : ""}{entry.points}
                    </span>
                    <span className="text-xs text-neutral-400 font-mono">
                      {t(`profile.pointActions.${entry.action}`, entry.action)}
                    </span>
                  </div>
                  <span className="text-[10px] text-neutral-700 font-mono tabular-nums shrink-0">
                    {new Date(entry.created_at).toLocaleDateString()}
                  </span>
                </div>
              ))
            )}
          </div>
        )}

        <PricingModal
          open={showPricing}
          onClose={() => { setShowPricing(false); loadSub(); }}
          currentPlan={sub?.plan}
        />
      </div>
    </div>
  );
}
