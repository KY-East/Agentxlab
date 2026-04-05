import { useState, useEffect, useCallback } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { api } from "../api/client";
import { useAuth } from "../contexts/AuthContext";
import type { ForumPost, LeaderboardEntry } from "../types";
import { MessageSquare, ThumbsUp, Plus } from "lucide-react";

const STATUS_COLORS: Record<string, string> = {
  open: "text-neutral-500",
  theory_ready: "text-blue-400",
  experimenting: "text-yellow-500",
  verified: "text-green-400",
  falsified: "text-red-500",
};

export default function Forum() {
  const { t, i18n } = useTranslation();
  const [params, setParams] = useSearchParams();
  const navigate = useNavigate();
  const { user } = useAuth();

  const ZONE_TABS = [
    { key: "ai_generated", label: t("forum.zoneAI") },
    { key: "community", label: t("forum.zoneCommunity") },
  ] as const;

  const SORT_OPTIONS = [
    { key: "newest", label: t("forum.sortNewest") },
    { key: "top", label: t("forum.sortTopVoted") },
    { key: "hot", label: t("forum.sortHottest") },
  ];

  const STATUS_LABELS: Record<string, string> = {
    open: t("forum.postStatus.open"),
    theory_ready: t("forum.postStatus.theory_ready"),
    experimenting: t("forum.postStatus.experimenting"),
    verified: t("forum.postStatus.verified"),
    falsified: t("forum.postStatus.falsified"),
  };

  const zone = (params.get("zone") || "ai_generated") as "ai_generated" | "community";
  const [sort, setSort] = useState("newest");
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [tagFilter, setTagFilter] = useState<string>("");
  const [posts, setPosts] = useState<ForumPost[]>([]);
  const [loading, setLoading] = useState(true);
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [forumStats, setForumStats] = useState<{
    total_posts: number;
    ai_posts: number;
    community_posts: number;
    experiment_posts: number;
    verified_posts: number;
    total_comments: number;
  } | null>(null);
  const [hotTags, setHotTags] = useState<{ tag: string; count: number }[]>([]);
  const [showNewPost, setShowNewPost] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newContent, setNewContent] = useState("");
  const [newType, setNewType] = useState("discussion");
  const [posting, setPosting] = useState(false);

  const fetchPosts = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.listForumPosts({
        zone,
        sort,
        status: statusFilter || undefined,
        discipline_tag: tagFilter || undefined,
      });
      setPosts(data);
    } catch {
      setPosts([]);
    } finally {
      setLoading(false);
    }
  }, [zone, sort, statusFilter, tagFilter]);

  useEffect(() => {
    fetchPosts();
  }, [fetchPosts]);

  useEffect(() => {
    api.getLeaderboard(10).then(setLeaderboard).catch(() => {});
    api.getForumStats().then(setForumStats).catch(() => {});
    api.getHotTags(10).then(setHotTags).catch(() => {});
  }, []);

  const handleTabChange = (z: string) => {
    setParams({ zone: z });
  };

  const [postError, setPostError] = useState("");

  const handleCreatePost = async () => {
    if (!newTitle.trim() || !newContent.trim()) return;
    setPosting(true);
    setPostError("");
    try {
      await api.createForumPost({
        title: newTitle.trim(),
        content: newContent.trim(),
        post_type: newType,
      });
      setShowNewPost(false);
      setNewTitle("");
      setNewContent("");
      fetchPosts();
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : t("forum.publishFailed");
      setPostError(msg);
    } finally {
      setPosting(false);
    }
  };

  return (
    <div className="h-full flex overflow-hidden">
      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Tab bar */}
        <div className="flex items-center gap-6 px-6 py-0 border-b-2 border-neutral-800 shrink-0">
          <div className="flex items-center gap-0">
            {ZONE_TABS.map((tab) => (
              <button
                key={tab.key}
                onClick={() => handleTabChange(tab.key)}
                className={`font-mono text-xs tracking-wider px-4 py-3 transition-colors ${
                  zone === tab.key
                    ? "border-b-2 border-cyan-400 text-white -mb-[2px]"
                    : "text-neutral-500 hover:text-white border-b-2 border-transparent -mb-[2px]"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          <div className="flex-1" />

          {/* Sort */}
          <div className="flex items-center gap-0">
            {SORT_OPTIONS.map((s) => (
              <button
                key={s.key}
                onClick={() => setSort(s.key)}
                className={`font-mono text-[10px] tracking-wider px-2 py-1 transition-colors ${
                  sort === s.key
                    ? "text-white bg-neutral-800"
                    : "text-neutral-600 hover:text-neutral-300"
                }`}
              >
                {s.label}
              </button>
            ))}
          </div>

          {/* Status filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-transparent border border-neutral-800 px-2 py-1 font-mono text-[10px] text-neutral-400 uppercase tracking-wider focus:outline-none focus:border-cyan-400"
          >
            <option value="">{t("forum.allStatus")}</option>
            {Object.entries(STATUS_LABELS).map(([k, v]) => (
              <option key={k} value={k}>{v}</option>
            ))}
          </select>

          {/* New Post button */}
          {zone === "community" && user && (
            <button
              onClick={() => setShowNewPost(true)}
              className="flex items-center gap-1 px-3 py-1.5 bg-cyan-400 text-black font-mono text-[10px] font-bold uppercase tracking-wider hover:bg-cyan-300 transition-colors"
            >
              <Plus size={12} />
              {t("forum.newPost")}
            </button>
          )}
        </div>

        {/* Active tag filter */}
        {tagFilter && (
          <div className="px-6 py-2 flex items-center gap-2 border-b border-neutral-800 shrink-0">
            <span className="font-mono text-[10px] text-neutral-600 uppercase tracking-wider">Filter:</span>
            <span className="font-mono text-[10px] px-2 py-0.5 bg-cyan-400/10 text-cyan-400 flex items-center gap-1">
              {tagFilter}
              <button onClick={() => setTagFilter("")} className="hover:text-white ml-1 text-xs">&times;</button>
            </span>
          </div>
        )}

        {/* Post list */}
        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <div className="px-6 py-12 font-mono text-xs text-neutral-600 animate-blink">
              [{t("common.loading")}]
            </div>
          ) : posts.length === 0 ? (
            <div className="px-6 py-12 font-mono text-xs text-neutral-600">
              {zone === "ai_generated"
                ? t("forum.emptyAIGenerated")
                : t("forum.emptyCommunity")}
            </div>
          ) : (
            <div className="divide-y divide-neutral-800">
              {posts.map((post) => (
                <PostRow
                  key={post.id}
                  post={post}
                  navigate={navigate}
                  statusLabels={STATUS_LABELS}
                />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Sidebar */}
      <div className="w-60 shrink-0 border-l-2 border-neutral-800 overflow-y-auto hidden lg:block">
        {/* Leaderboard */}
        <div className="border-b border-neutral-800 p-4">
          <h3 className="font-mono text-[10px] uppercase tracking-[0.2em] text-neutral-600 mb-3">
            {t("forum.leaderboard")}
          </h3>
          {leaderboard.length === 0 ? (
            <p className="font-mono text-[10px] text-neutral-700">--</p>
          ) : (
            <div className="divide-y divide-neutral-800/50">
              {leaderboard.map((entry, i) => (
                <div
                  key={entry.user_id}
                  className="flex items-center gap-2 py-1.5 text-xs"
                >
                  <span
                    className={`font-mono w-4 text-right text-[10px] ${
                      i === 0
                        ? "text-cyan-400 font-bold"
                        : i < 3
                        ? "text-neutral-400"
                        : "text-neutral-600"
                    }`}
                  >
                    {i + 1}
                  </span>
                  {entry.avatar_url ? (
                    <img
                      src={entry.avatar_url}
                      alt=""
                      className="w-4 h-4 rounded-sm"
                    />
                  ) : (
                    <div className="w-4 h-4 rounded-sm bg-neutral-800 flex items-center justify-center font-mono text-[8px] text-neutral-500">
                      {entry.display_name.charAt(0)}
                    </div>
                  )}
                  <span className="flex-1 truncate text-neutral-400 text-[11px]">
                    {entry.display_name}
                  </span>
                  <span className="font-mono text-[10px] text-cyan-400">
                    {entry.points.toLocaleString(i18n.language === "zh" ? "zh-CN" : "en-US")}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Stats */}
        {forumStats && (
          <div className="border-b border-neutral-800 p-4">
            <h3 className="font-mono text-[10px] uppercase tracking-[0.2em] text-neutral-600 mb-3">
              {t("forum.forumStats")}
            </h3>
            <div className="grid grid-cols-2 gap-px bg-neutral-800">
              {[
                { n: forumStats.total_posts, l: t("forum.totalPosts"), c: "text-white" },
                { n: forumStats.total_comments, l: t("forum.totalComments"), c: "text-white" },
                { n: forumStats.verified_posts, l: t("forum.verifiedCount"), c: "text-green-400" },
                { n: forumStats.experiment_posts, l: t("forum.experimentCount"), c: "text-yellow-500" },
              ].map((s) => (
                <div key={s.l} className="bg-[#0a0a0a] p-2 text-center">
                  <p className={`font-mono text-lg font-bold ${s.c}`}>{s.n}</p>
                  <p className="font-mono text-[8px] text-neutral-600 uppercase tracking-wider">{s.l}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Hot Tags */}
        {hotTags.length > 0 && (
          <div className="p-4">
            <h3 className="font-mono text-[10px] uppercase tracking-[0.2em] text-neutral-600 mb-3">
              {t("forum.hotTags")}
            </h3>
            <div className="flex flex-wrap gap-1">
              {hotTags.map((ht) => (
                <button
                  key={ht.tag}
                  onClick={() => setTagFilter((prev) => (prev === ht.tag ? "" : ht.tag))}
                  className={`font-mono text-[10px] px-2 py-0.5 transition-colors ${
                    tagFilter === ht.tag
                      ? "bg-cyan-400/10 text-cyan-400 border border-cyan-400/30"
                      : "text-neutral-500 border border-neutral-800 hover:border-neutral-600"
                  }`}
                >
                  {ht.tag} {ht.count}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* New post modal */}
      {showNewPost && (
        <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4">
          <div className="bg-[#0a0a0a] border-2 border-neutral-800 w-full max-w-lg p-6 space-y-4">
            <h2 className="font-mono text-sm font-bold uppercase tracking-wider text-white">
              {t("forum.newPostTitle")}
            </h2>

            <div>
              <label className="font-mono text-[10px] text-neutral-600 uppercase tracking-wider block mb-1">Type</label>
              <select
                value={newType}
                onChange={(e) => setNewType(e.target.value)}
                className="w-full bg-transparent border border-neutral-800 px-3 py-2 font-mono text-xs text-neutral-300 focus:outline-none focus:border-cyan-400"
              >
                <option value="discussion">{t("forum.postTypes.discussion")}</option>
                <option value="question">{t("forum.postTypes.question")}</option>
                <option value="experiment_result">{t("forum.postTypes.experiment_result")}</option>
              </select>
            </div>

            <div>
              <label className="font-mono text-[10px] text-neutral-600 uppercase tracking-wider block mb-1">Title</label>
              <input
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                placeholder={t("forum.titlePlaceholder")}
                className="w-full bg-transparent border border-neutral-800 px-3 py-2 font-mono text-xs text-white placeholder-neutral-700 focus:outline-none focus:border-cyan-400"
              />
            </div>

            <div>
              <label className="font-mono text-[10px] text-neutral-600 uppercase tracking-wider block mb-1">
                {t("forum.content")}
              </label>
              <textarea
                value={newContent}
                onChange={(e) => setNewContent(e.target.value)}
                placeholder={t("forum.contentPlaceholder")}
                rows={8}
                className="w-full bg-transparent border border-neutral-800 px-3 py-2 text-xs text-neutral-300 placeholder-neutral-700 focus:outline-none focus:border-cyan-400 resize-none"
              />
            </div>

            <div className="flex justify-end gap-2">
              <button
                onClick={() => setShowNewPost(false)}
                className="font-mono text-xs text-neutral-500 hover:text-white px-4 py-2 transition-colors"
              >
                {t("common.cancel")}
              </button>
              <button
                onClick={handleCreatePost}
                disabled={posting || !newTitle.trim() || !newContent.trim()}
                className="font-mono text-xs font-bold uppercase tracking-wider px-4 py-2 bg-cyan-400 text-black hover:bg-cyan-300 disabled:opacity-50 transition-colors"
              >
                {posting ? t("forum.publishing") : t("forum.publish")}
              </button>
            </div>
            {postError && (
              <p className="font-mono text-[10px] text-red-500 mt-2">{postError}</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function PostRow({
  post,
  navigate,
  statusLabels,
}: {
  post: ForumPost;
  navigate: (path: string) => void;
  statusLabels: Record<string, string>;
}) {
  const { i18n } = useTranslation();
  return (
    <button
      onClick={() => navigate(`/forum/${post.id}`)}
      className="w-full text-left px-6 py-3 hover:bg-neutral-900/50 transition-colors group flex items-start gap-4 border-l-2 border-transparent hover:border-cyan-400"
    >
      {/* Vote score */}
      <div className="flex flex-col items-center pt-0.5 shrink-0 min-w-[32px]">
        <span className="font-mono text-sm font-bold text-neutral-400 group-hover:text-white transition-colors">
          {post.vote_score}
        </span>
        <span className="font-mono text-[8px] text-neutral-700 uppercase">pts</span>
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-0.5 flex-wrap">
          {post.is_pinned && (
            <span className="font-mono text-[9px] text-cyan-400 uppercase tracking-wider">PIN</span>
          )}
          <span
            className={`font-mono text-[9px] uppercase tracking-wider ${
              STATUS_COLORS[post.status] || "text-neutral-500"
            }`}
          >
            {statusLabels[post.status] || post.status}
          </span>
          {post.zone === "ai_generated" && (
            <span className="font-mono text-[9px] text-cyan-400 uppercase tracking-wider">
              AI
            </span>
          )}
        </div>

        <h3 className="text-sm text-neutral-300 group-hover:text-white truncate transition-colors">
          {post.title}
        </h3>

        <div className="flex items-center gap-3 mt-1 font-mono text-[10px] text-neutral-600">
          {post.author && (
            <span>{post.author.display_name}</span>
          )}
          {!post.author && post.zone === "ai_generated" && (
            <span className="text-cyan-400/60">Agent X Lab</span>
          )}
          <span className="flex items-center gap-0.5">
            <MessageSquare size={9} /> {post.comment_count}
          </span>
          <span className="flex items-center gap-0.5">
            <ThumbsUp size={9} /> {post.vote_score}
          </span>
          {post.discipline_tags && post.discipline_tags.length > 0 && (
            <span className="truncate max-w-[150px] text-neutral-700">
              {post.discipline_tags.slice(0, 3).join(" / ")}
            </span>
          )}
          <span className="ml-auto">
            {new Date(post.created_at).toLocaleDateString(
              i18n.language === "zh" ? "zh-CN" : "en-US"
            )}
          </span>
        </div>
      </div>
    </button>
  );
}
