import { useState, useEffect, useCallback, useMemo } from "react";
import { useTranslation } from "react-i18next";
import { useParams, useNavigate, Link } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { api } from "../api/client";
import { useAuth } from "../contexts/AuthContext";
import type { ForumPost, ForumComment as ForumCommentType } from "../types";
import {
  ArrowLeft,
  ChevronUp,
  ChevronDown,
  MessageSquare,
  Send,
  FlaskConical,
  Pencil,
  Trash2,
  Loader2,
  Award,
  CheckCircle2,
  XCircle,
  HelpCircle,
  Users,
  Languages,
} from "lucide-react";

const STATUS_COLORS: Record<string, string> = {
  open: "text-neutral-500",
  theory_ready: "text-blue-400",
  experimenting: "text-yellow-500",
  verified: "text-green-400",
  falsified: "text-red-500",
};

const EXPERIMENT_STEPS = ["open", "experimenting", "verified"] as const;

const isExperimentPost = (pt: string) =>
  pt === "experiment_request" || pt === "experiment_result";

export default function ForumPostDetail() {
  const { t, i18n } = useTranslation();
  const { postId } = useParams<{ postId: string }>();
  const navigate = useNavigate();
  const { user, setShowAuthModal } = useAuth();

  const [post, setPost] = useState<ForumPost | null>(null);
  const [comments, setComments] = useState<ForumCommentType[]>([]);
  const [loading, setLoading] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [commentText, setCommentText] = useState("");
  const [replyTo, setReplyTo] = useState<number | null>(null);
  const [commentType, setCommentType] = useState<string>("normal");
  const [sending, setSending] = useState(false);
  const [commentError, setCommentError] = useState<string | null>(null);
  const [postVote, setPostVote] = useState<number | null>(null);
  const [voteError, setVoteError] = useState<string | null>(null);

  const [editing, setEditing] = useState(false);
  const [editTitle, setEditTitle] = useState("");
  const [editContent, setEditContent] = useState("");
  const [editSaving, setEditSaving] = useState(false);

  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const [showSubmitResult, setShowSubmitResult] = useState(false);
  const [resultVerdict, setResultVerdict] = useState<string>("verified");
  const [resultContent, setResultContent] = useState("");
  const [resultSubmitting, setResultSubmitting] = useState(false);

  const [postTranslation, setPostTranslation] = useState<Record<string, string> | null>(null);
  const [postTranslating, setPostTranslating] = useState(false);
  const [commentTranslations, setCommentTranslations] = useState<Record<number, string>>({});
  const [commentTranslating, setCommentTranslating] = useState<Record<number, boolean>>({});

  const id = Number(postId);

  const fetchData = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    setFetchError(null);
    try {
      const [p, c] = await Promise.all([
        api.getForumPost(id),
        api.getForumComments(id),
      ]);
      setPost(p);
      setComments(c);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      if (msg.includes("404")) {
        setPost(null);
      } else {
        setFetchError(t("forum.loadFailed"));
      }
    } finally {
      setLoading(false);
    }
  }, [id, t]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const claimers = useMemo(() => {
    const all: ForumCommentType[] = [];
    const walk = (list: ForumCommentType[]) => {
      for (const c of list) {
        if (c.comment_type === "claim_experiment" && c.author) all.push(c);
        if (c.children) walk(c.children);
      }
    };
    walk(comments);
    return all;
  }, [comments]);

  const handleVote = async (voteType: 1 | -1) => {
    if (!user) { setShowAuthModal(true); return; }
    if (!post) return;
    setVoteError(null);
    try {
      const res = await api.forumVote({ target_type: "post", target_id: post.id, vote_type: voteType });
      setPost((p) => (p ? { ...p, vote_score: res.new_score } : p));
      setPostVote(res.user_vote);
    } catch {
      setVoteError(t("forum.voteFailed"));
      setTimeout(() => setVoteError(null), 3000);
    }
  };

  const handleComment = async () => {
    if (!user) { setShowAuthModal(true); return; }
    if (!commentText.trim()) return;
    setSending(true);
    setCommentError(null);
    try {
      await api.createForumComment(id, {
        content: commentText.trim(),
        parent_id: replyTo ?? undefined,
        comment_type: commentType,
      });
      setCommentText("");
      setReplyTo(null);
      setCommentType("normal");
      const [p, c] = await Promise.all([api.getForumPost(id), api.getForumComments(id)]);
      setPost(p);
      setComments(c);
    } catch {
      setCommentError(t("forum.commentFailed"));
    } finally {
      setSending(false);
    }
  };

  const handleSubmitResult = async () => {
    if (!user || !resultContent.trim()) return;
    setResultSubmitting(true);
    try {
      await api.createForumComment(id, {
        content: resultContent.trim(),
        comment_type: "submit_result",
        result_verdict: resultVerdict,
      });
      setShowSubmitResult(false);
      setResultContent("");
      const [p, c] = await Promise.all([api.getForumPost(id), api.getForumComments(id)]);
      setPost(p);
      setComments(c);
    } catch {
      setCommentError(t("forum.commentFailed"));
    } finally {
      setResultSubmitting(false);
    }
  };

  const handleEdit = () => {
    if (!post) return;
    setEditTitle(post.title);
    setEditContent(post.content);
    setEditing(true);
  };

  const handleEditSave = async () => {
    if (!post) return;
    setEditSaving(true);
    try {
      const updated = await api.updateForumPost(post.id, { title: editTitle.trim(), content: editContent.trim() });
      setPost(updated);
      setEditing(false);
    } catch { /* keep editing open */ } finally {
      setEditSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!post) return;
    setDeleting(true);
    try {
      await api.deleteForumPost(post.id);
      navigate("/forum");
    } catch {
      setShowDeleteConfirm(false);
      alert(t("forum.deleteFailed"));
    } finally {
      setDeleting(false);
    }
  };

  const targetLang = i18n.language?.startsWith("zh") ? "en" : "zh";

  const handleTranslatePost = async () => {
    if (!post || postTranslating) return;
    if (postTranslation) {
      setPostTranslation(null);
      return;
    }
    setPostTranslating(true);
    try {
      const res = await api.translateContent({
        content_type: "post",
        content_id: post.id,
        fields: ["title", "content"],
        target_lang: targetLang,
      });
      setPostTranslation(res.translations);
    } catch {
      /* silent */
    } finally {
      setPostTranslating(false);
    }
  };

  const handleTranslateComment = async (commentId: number) => {
    if (commentTranslating[commentId]) return;
    if (commentTranslations[commentId]) {
      setCommentTranslations((prev) => {
        const next = { ...prev };
        delete next[commentId];
        return next;
      });
      return;
    }
    setCommentTranslating((prev) => ({ ...prev, [commentId]: true }));
    try {
      const res = await api.translateContent({
        content_type: "comment",
        content_id: commentId,
        fields: ["content"],
        target_lang: targetLang,
      });
      setCommentTranslations((prev) => ({ ...prev, [commentId]: res.translations.content }));
    } catch {
      /* silent */
    } finally {
      setCommentTranslating((prev) => ({ ...prev, [commentId]: false }));
    }
  };

  const isOwner = user && post && post.user_id === user.id;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 size={16} className="animate-spin text-neutral-600" />
      </div>
    );
  }
  if (fetchError) {
    return (
      <div className="p-8 space-y-3">
        <p className="font-mono text-xs text-red-400">{fetchError}</p>
        <button onClick={fetchData} className="font-mono text-xs text-cyan-400 hover:text-white underline transition-colors">
          {t("common.retry", "Retry")}
        </button>
      </div>
    );
  }
  if (!post) {
    return <div className="p-8 font-mono text-xs text-neutral-600">{t("forum.postNotFound")}</div>;
  }

  const isExp = isExperimentPost(post.post_type);

  return (
    <div className="h-full overflow-y-auto bg-neutral-950">
      <div className="max-w-3xl mx-auto px-6 py-6 space-y-6">
        {/* Back */}
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-1 font-mono text-[10px] text-neutral-600 hover:text-white uppercase tracking-wider transition-colors"
        >
          <ArrowLeft size={10} /> {t("forum.backToForum")}
        </button>

        {/* --- EXPERIMENT CARD --- */}
        {isExp && (
          <ExperimentCard post={post} claimers={claimers} t={t} />
        )}

        {/* Post header */}
        <div className="flex gap-4">
          <div className="flex flex-col items-center gap-0.5 pt-1 shrink-0">
            <button onClick={() => handleVote(1)} className={`transition-colors ${postVote === 1 ? "text-cyan-400" : "text-neutral-600 hover:text-cyan-400"}`}>
              <ChevronUp size={18} />
            </button>
            <span className="font-mono text-base font-bold text-neutral-300 tabular-nums">{post.vote_score}</span>
            <button onClick={() => handleVote(-1)} className={`transition-colors ${postVote === -1 ? "text-red-400" : "text-neutral-600 hover:text-red-400"}`}>
              <ChevronDown size={18} />
            </button>
            {voteError && <span className="font-mono text-[8px] text-red-400 mt-1">{voteError}</span>}
          </div>

          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap mb-2">
              <span className={`font-mono text-[9px] uppercase tracking-wider ${STATUS_COLORS[post.status] || "text-neutral-500"}`}>
                {t(`forum.postStatus.${post.status}`, post.status)}
              </span>
              {post.zone === "ai_generated" && (
                <span className="font-mono text-[9px] uppercase tracking-wider text-cyan-400">AI</span>
              )}
              <span className="font-mono text-[9px] text-neutral-600 uppercase tracking-wider">
                {t(`forum.postTypes.${post.post_type}`, post.post_type)}
              </span>
              {post.debate_id && (
                <Link to={`/debate/${post.debate_id}`} className="font-mono text-[9px] text-cyan-400 hover:text-white underline transition-colors">
                  {t("forum.viewDebate", { id: post.debate_id })}
                </Link>
              )}
            </div>

            {editing ? (
              <div className="space-y-3">
                <input value={editTitle} onChange={(e) => setEditTitle(e.target.value)} className="w-full bg-transparent border border-neutral-700 focus:border-cyan-400 px-3 py-2 text-sm text-white font-mono outline-none" />
                <textarea value={editContent} onChange={(e) => setEditContent(e.target.value)} rows={12} className="w-full bg-transparent border border-neutral-700 focus:border-cyan-400 px-3 py-2 text-xs text-neutral-300 font-mono outline-none resize-none" />
                <div className="flex gap-2">
                  <button onClick={handleEditSave} disabled={editSaving} className="px-3 py-1 border border-cyan-400 text-cyan-400 text-[10px] font-mono uppercase tracking-wider hover:bg-cyan-400/10 disabled:opacity-40">
                    {editSaving ? t("profile.saving") : t("profile.save")}
                  </button>
                  <button onClick={() => setEditing(false)} className="px-3 py-1 border border-neutral-700 text-neutral-500 text-[10px] font-mono uppercase tracking-wider hover:text-white">
                    {t("forum.cancel")}
                  </button>
                </div>
              </div>
            ) : (
              <>
                <h1 className="text-lg font-bold text-white">{post.title}</h1>
                <div className="flex items-center gap-3 mt-2 font-mono text-[10px] text-neutral-600">
                  {post.author ? (
                    <span className="flex items-center gap-1">
                      {post.author.avatar_url && <img src={post.author.avatar_url} alt="" className="w-3.5 h-3.5" />}
                      {post.author.display_name}
                    </span>
                  ) : (
                    <span className="text-cyan-400/60">Agent X Lab</span>
                  )}
                  <span>{new Date(post.created_at).toLocaleString(i18n.language === "zh" ? "zh-CN" : "en-US")}</span>
                  {post.discipline_tags && <span className="text-neutral-700">{post.discipline_tags.join(" / ")}</span>}
                  {isOwner && (
                    <div className="ml-auto flex items-center gap-2">
                      <button onClick={handleEdit} className="flex items-center gap-1 text-neutral-600 hover:text-cyan-400 transition-colors">
                        <Pencil size={10} /><span className="uppercase tracking-wider">{t("forum.edit")}</span>
                      </button>
                      <button onClick={() => setShowDeleteConfirm(true)} className="flex items-center gap-1 text-neutral-600 hover:text-red-400 transition-colors">
                        <Trash2 size={10} /><span className="uppercase tracking-wider">{t("forum.delete")}</span>
                      </button>
                    </div>
                  )}
                </div>
              </>
            )}
          </div>
        </div>

        {/* Post body */}
        {!editing && (
          <div className="border-l-2 border-neutral-800 pl-4 py-2">
            <div className="prose prose-invert prose-sm max-w-none prose-headings:font-mono prose-headings:text-white prose-p:text-neutral-300 prose-a:text-cyan-400 prose-strong:text-white prose-code:text-cyan-300 prose-code:bg-neutral-900 prose-code:px-1 prose-pre:bg-neutral-900 prose-pre:border prose-pre:border-neutral-800 prose-li:text-neutral-300 prose-hr:border-neutral-800">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{post.content}</ReactMarkdown>
            </div>

            {postTranslation && (
              <div className="mt-3 border border-dashed border-cyan-800/50 p-3 bg-cyan-950/10">
                {postTranslation.title && (
                  <h3 className="text-sm font-mono font-bold text-cyan-300 mb-2">{postTranslation.title}</h3>
                )}
                <div className="prose prose-invert prose-sm max-w-none prose-headings:font-mono prose-headings:text-white prose-p:text-neutral-300 prose-a:text-cyan-400 prose-strong:text-white prose-code:text-cyan-300 prose-code:bg-neutral-900 prose-code:px-1 prose-pre:bg-neutral-900 prose-pre:border prose-pre:border-neutral-800 prose-li:text-neutral-300 prose-hr:border-neutral-800">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{postTranslation.content || ""}</ReactMarkdown>
                </div>
              </div>
            )}

            <button
              onClick={handleTranslatePost}
              disabled={postTranslating}
              className="mt-2 flex items-center gap-1.5 text-[11px] font-mono text-neutral-500 hover:text-cyan-400 transition-colors disabled:opacity-40"
            >
              <Languages size={12} />
              {postTranslating
                ? t("forum.translating")
                : postTranslation
                  ? t("forum.showOriginal")
                  : t("forum.translatePost")}
            </button>
          </div>
        )}

        {/* --- SUBMIT RESULT FORM (experiment posts only) --- */}
        {isExp && post.status === "experimenting" && user && !showSubmitResult && (
          <button
            onClick={() => setShowSubmitResult(true)}
            className="w-full flex items-center justify-center gap-2 py-3 border-2 border-dashed border-yellow-500/40 text-yellow-500 font-mono text-xs uppercase tracking-wider hover:border-yellow-500 hover:bg-yellow-500/5 transition-colors"
          >
            <FlaskConical size={14} />
            {t("forum.experiment.submitResult")}
          </button>
        )}

        {showSubmitResult && (
          <SubmitResultForm
            verdict={resultVerdict}
            onVerdictChange={setResultVerdict}
            content={resultContent}
            onContentChange={setResultContent}
            submitting={resultSubmitting}
            onSubmit={handleSubmitResult}
            onCancel={() => setShowSubmitResult(false)}
            t={t}
          />
        )}

        {/* Comment box */}
        <div className="border-2 border-neutral-800 p-4 space-y-3">
          {replyTo && (
            <div className="font-mono text-[10px] text-neutral-500 flex items-center gap-2">
              {t("forum.replyingTo", { id: replyTo })}
              <button onClick={() => setReplyTo(null)} className="text-red-500 hover:text-red-400 transition-colors uppercase tracking-wider">
                {t("forum.cancel")}
              </button>
            </div>
          )}

          <div className="flex items-center gap-2">
            {["experiment_request", "experiment_result"].includes(post.post_type) && user && (
              <select
                value={commentType}
                onChange={(e) => setCommentType(e.target.value)}
                className="bg-transparent border border-neutral-800 px-2 py-1.5 font-mono text-[10px] text-neutral-400 uppercase focus:outline-none focus:border-cyan-400"
              >
                <option value="normal">{t("forum.commentTypes.normal")}</option>
                <option value="claim_experiment">{t("forum.commentTypes.claim_direction")}</option>
              </select>
            )}
          </div>

          <div className="flex gap-2">
            <textarea
              value={commentText}
              onChange={(e) => setCommentText(e.target.value)}
              placeholder={!user ? t("forum.loginToInteract") : commentType === "claim_experiment" ? t("forum.describeVerifyPlaceholder") : t("forum.commentPlaceholder")}
              disabled={!user}
              rows={3}
              className="flex-1 bg-transparent border border-neutral-800 px-3 py-2 text-sm text-neutral-300 placeholder-neutral-700 resize-none focus:outline-none focus:border-cyan-400 disabled:opacity-50"
            />
            <button
              onClick={handleComment}
              disabled={sending || !commentText.trim() || !user}
              className="self-end px-3 py-2 bg-cyan-400 text-black hover:bg-cyan-300 disabled:opacity-50 transition-colors"
            >
              {commentType === "claim_experiment" ? <FlaskConical size={14} /> : <Send size={14} />}
            </button>
          </div>
          {commentError && <p className="font-mono text-[10px] text-red-400">{commentError}</p>}
        </div>

        {/* Comments */}
        <div className="space-y-0">
          <h2 className="font-mono text-[10px] uppercase tracking-[0.2em] text-neutral-600 flex items-center gap-1.5 mb-3">
            <MessageSquare size={11} />
            {t("forum.comments", { count: post.comment_count })}
          </h2>
          {comments.length === 0 ? (
            <p className="font-mono text-[10px] text-neutral-700 py-4">{t("forum.noComments")}</p>
          ) : (
            <div className="divide-y divide-neutral-800/50">
              {comments.map((c) => (
                <CommentTree
                  key={c.id}
                  comment={c}
                  depth={0}
                  onReply={(cid) => setReplyTo(cid)}
                  user={user}
                  onScoreChange={(cid, score, uv) => {
                    setComments((prev) => updateComment(prev, cid, score, uv));
                  }}
                  translations={commentTranslations}
                  translating={commentTranslating}
                  onTranslate={handleTranslateComment}
                />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Delete confirm */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4">
          <div className="bg-[#0a0a0a] border-2 border-neutral-800 p-6 space-y-4 max-w-sm w-full">
            <p className="font-mono text-xs text-neutral-300">{t("forum.confirmDelete")}</p>
            <div className="flex justify-end gap-2">
              <button onClick={() => setShowDeleteConfirm(false)} className="font-mono text-xs text-neutral-500 hover:text-white px-4 py-2 transition-colors">
                {t("forum.cancel")}
              </button>
              <button onClick={handleDelete} disabled={deleting} className="font-mono text-xs font-bold uppercase tracking-wider px-4 py-2 bg-red-500 text-white hover:bg-red-400 disabled:opacity-50 transition-colors">
                {t("forum.delete")}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

/* ─────────────────── ExperimentCard ─────────────────── */

function ExperimentCard({
  post,
  claimers,
  t,
}: {
  post: ForumPost;
  claimers: ForumCommentType[];
  t: (k: string, opts?: Record<string, unknown>) => string;
}) {
  const stepIdx = post.status === "verified" || post.status === "falsified"
    ? 2
    : post.status === "experimenting"
    ? 1
    : 0;

  const statusKey =
    post.status === "verified" ? "statusVerified"
    : post.status === "falsified" ? "statusFalsified"
    : post.status === "experimenting" ? "statusExperimenting"
    : "statusOpen";

  const rewardText =
    post.status === "verified" ? t("forum.experiment.verifiedReward")
    : post.status === "falsified" ? t("forum.experiment.falsifiedReward")
    : null;

  return (
    <div className="border-2 border-yellow-500/30 bg-yellow-500/5 p-4 space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <FlaskConical size={14} className="text-yellow-500" />
          <span className="font-mono text-[10px] uppercase tracking-wider text-yellow-500 font-bold">
            {t(`forum.postTypes.${post.post_type}`, post.post_type)}
          </span>
        </div>
        {post.debate_id && (
          <Link
            to={`/debate/${post.debate_id}`}
            className="font-mono text-[10px] text-cyan-400 hover:text-white transition-colors"
          >
            {t("forum.experiment.fromDebate", { id: post.debate_id })}
          </Link>
        )}
        {!post.debate_id && post.spark_id && (
          <span className="font-mono text-[10px] text-neutral-600">
            {t("forum.experiment.fromSpark")}
          </span>
        )}
      </div>

      {/* Progress bar */}
      <div className="flex items-center gap-0">
        {EXPERIMENT_STEPS.map((step, i) => {
          const isActive = i <= stepIdx;
          const isFalsified = post.status === "falsified" && i === 2;
          const label =
            step === "open" ? t("forum.experiment.statusOpen")
            : step === "experimenting" ? t("forum.experiment.statusExperimenting")
            : isFalsified ? t("forum.experiment.statusFalsified")
            : t("forum.experiment.statusVerified");

          return (
            <div key={step} className="flex-1 flex flex-col items-center">
              <div className="flex items-center w-full">
                {i > 0 && (
                  <div className={`flex-1 h-px ${isActive ? (isFalsified ? "bg-red-500" : "bg-yellow-500") : "bg-neutral-800"}`} />
                )}
                <div
                  className={`w-5 h-5 flex items-center justify-center border-2 shrink-0 ${
                    isActive
                      ? isFalsified
                        ? "border-red-500 bg-red-500/20"
                        : i === stepIdx
                        ? "border-yellow-500 bg-yellow-500/20"
                        : "border-green-500 bg-green-500/20"
                      : "border-neutral-700 bg-transparent"
                  }`}
                >
                  {isActive && i < stepIdx && <CheckCircle2 size={10} className="text-green-400" />}
                  {isActive && i === stepIdx && !isFalsified && (
                    step === "verified"
                      ? <CheckCircle2 size={10} className="text-green-400" />
                      : <div className="w-1.5 h-1.5 bg-yellow-500" />
                  )}
                  {isFalsified && <XCircle size={10} className="text-red-400" />}
                </div>
                {i < EXPERIMENT_STEPS.length - 1 && (
                  <div className={`flex-1 h-px ${i < stepIdx ? "bg-yellow-500" : "bg-neutral-800"}`} />
                )}
              </div>
              <span className={`font-mono text-[8px] mt-1 uppercase tracking-wider ${isActive ? (isFalsified ? "text-red-400" : "text-yellow-400") : "text-neutral-700"}`}>
                {label}
              </span>
            </div>
          );
        })}
      </div>

      {/* Claimers + Reward */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Users size={11} className="text-neutral-600" />
          {claimers.length === 0 ? (
            <span className="font-mono text-[10px] text-neutral-600">{t("forum.experiment.noClaims")}</span>
          ) : (
            <div className="flex items-center gap-1">
              <span className="font-mono text-[10px] text-neutral-500">{t("forum.experiment.claimedBy")}:</span>
              {claimers.slice(0, 5).map((c) => (
                <span key={c.id} className="font-mono text-[10px] text-neutral-300">
                  {c.author?.avatar_url ? (
                    <img src={c.author.avatar_url} alt="" className="w-4 h-4 inline mr-0.5" />
                  ) : null}
                  {c.author?.display_name}
                </span>
              ))}
              {claimers.length > 5 && (
                <span className="font-mono text-[10px] text-neutral-600">+{claimers.length - 5}</span>
              )}
            </div>
          )}
        </div>

        {rewardText && (
          <div className="flex items-center gap-1">
            <Award size={11} className={post.status === "verified" ? "text-green-400" : "text-red-400"} />
            <span className={`font-mono text-xs font-bold tabular-nums ${post.status === "verified" ? "text-green-400" : "text-red-400"}`}>
              {rewardText}
            </span>
            <span className="font-mono text-[8px] text-neutral-600 uppercase">pts</span>
          </div>
        )}
      </div>
    </div>
  );
}

/* ─────────────────── SubmitResultForm ─────────────────── */

function SubmitResultForm({
  verdict,
  onVerdictChange,
  content,
  onContentChange,
  submitting,
  onSubmit,
  onCancel,
  t,
}: {
  verdict: string;
  onVerdictChange: (v: string) => void;
  content: string;
  onContentChange: (v: string) => void;
  submitting: boolean;
  onSubmit: () => void;
  onCancel: () => void;
  t: (k: string) => string;
}) {
  const verdicts = [
    { key: "verified", label: t("forum.experiment.verdictVerified"), icon: CheckCircle2, color: "text-green-400 border-green-500/40", reward: t("forum.experiment.verifiedReward") },
    { key: "falsified_inspiring", label: t("forum.experiment.verdictFalsified"), icon: XCircle, color: "text-red-400 border-red-500/40", reward: t("forum.experiment.falsifiedReward") },
    { key: "inconclusive", label: t("forum.experiment.verdictInconclusive"), icon: HelpCircle, color: "text-neutral-400 border-neutral-600", reward: t("forum.experiment.inconclusiveReward") },
  ];

  return (
    <div className="border-2 border-yellow-500/30 bg-neutral-950 p-5 space-y-4">
      <h3 className="font-mono text-xs font-bold uppercase tracking-wider text-yellow-500 flex items-center gap-2">
        <FlaskConical size={14} />
        {t("forum.experiment.submitResult")}
      </h3>

      <p className="font-mono text-[10px] text-neutral-500">
        {t("forum.experiment.submitResultDesc")}
      </p>

      {/* Verdict selector */}
      <div className="space-y-1.5">
        <label className="font-mono text-[10px] text-neutral-600 uppercase tracking-wider">
          {t("forum.experiment.verdictLabel")}
        </label>
        <div className="grid grid-cols-3 gap-2">
          {verdicts.map((v) => {
            const Icon = v.icon;
            const selected = verdict === v.key;
            return (
              <button
                key={v.key}
                onClick={() => onVerdictChange(v.key)}
                className={`p-3 border-2 text-left transition-colors ${
                  selected ? v.color + " bg-neutral-900" : "border-neutral-800 text-neutral-600 hover:border-neutral-700"
                }`}
              >
                <div className="flex items-center gap-1.5 mb-1">
                  <Icon size={12} />
                  <span className="font-mono text-[10px] uppercase tracking-wider font-bold">{v.label}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Award size={9} />
                  <span className="font-mono text-[10px] tabular-nums">{v.reward} pts</span>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Content */}
      <textarea
        value={content}
        onChange={(e) => onContentChange(e.target.value)}
        rows={10}
        placeholder="## Methods\n\n## Data\n\n## Conclusion"
        className="w-full bg-transparent border border-neutral-800 px-3 py-2 text-xs text-neutral-300 placeholder-neutral-700 font-mono resize-none focus:outline-none focus:border-yellow-500"
      />

      {/* Actions */}
      <div className="flex justify-end gap-2">
        <button
          onClick={onCancel}
          className="font-mono text-xs text-neutral-500 hover:text-white px-4 py-2 transition-colors"
        >
          {t("forum.cancel")}
        </button>
        <button
          onClick={onSubmit}
          disabled={submitting || !content.trim()}
          className="font-mono text-xs font-bold uppercase tracking-wider px-4 py-2 bg-yellow-500 text-black hover:bg-yellow-400 disabled:opacity-50 transition-colors"
        >
          {submitting ? t("forum.experiment.submitting") : t("forum.experiment.submit")}
        </button>
      </div>
    </div>
  );
}

/* ─────────────────── Comment helpers ─────────────────── */

function updateComment(
  comments: ForumCommentType[],
  targetId: number,
  newScore: number,
  userVote: number | null,
): ForumCommentType[] {
  return comments.map((c) => {
    if (c.id === targetId) return { ...c, vote_score: newScore, _userVote: userVote } as ForumCommentType;
    if (c.children?.length) return { ...c, children: updateComment(c.children, targetId, newScore, userVote) };
    return c;
  });
}

function CommentTree({
  comment,
  depth,
  onReply,
  user,
  onScoreChange,
  translations,
  translating,
  onTranslate,
}: {
  comment: ForumCommentType & { _userVote?: number | null };
  depth: number;
  onReply: (id: number) => void;
  user: { id: number } | null;
  onScoreChange: (commentId: number, newScore: number, userVote: number | null) => void;
  translations: Record<number, string>;
  translating: Record<number, boolean>;
  onTranslate: (commentId: number) => void;
}) {
  const { t, i18n } = useTranslation();
  const [voteError, setVoteError] = useState<string | null>(null);

  const handleVote = async (voteType: 1 | -1) => {
    if (!user) return;
    setVoteError(null);
    try {
      const res = await api.forumVote({ target_type: "comment", target_id: comment.id, vote_type: voteType });
      onScoreChange(comment.id, res.new_score, res.user_vote);
    } catch {
      setVoteError(t("forum.voteFailed"));
      setTimeout(() => setVoteError(null), 3000);
    }
  };

  const uv = (comment as { _userVote?: number | null })._userVote ?? null;
  const hasTranslation = translations[comment.id] !== undefined;
  const isTranslating = translating[comment.id] || false;

  return (
    <div className={`${depth > 0 ? "ml-5 border-l border-neutral-800 pl-3" : ""}`}>
      <div className="py-2.5">
        <div className="flex items-center gap-2 font-mono text-[10px] text-neutral-600 mb-1">
          {comment.author && (
            <span className="flex items-center gap-1">
              {comment.author.avatar_url && <img src={comment.author.avatar_url} alt="" className="w-3 h-3" />}
              <span className="text-neutral-400">{comment.author.display_name}</span>
            </span>
          )}
          <span>{new Date(comment.created_at).toLocaleString(i18n.language === "zh" ? "zh-CN" : "en-US")}</span>
          {comment.comment_type === "claim_experiment" && (
            <span className="uppercase tracking-wider text-yellow-500 font-bold">CLAIM</span>
          )}
          {comment.comment_type === "submit_result" && (
            <span className="uppercase tracking-wider text-green-400 font-bold">RESULT</span>
          )}
        </div>

        <div className="prose prose-invert prose-sm max-w-none prose-p:text-neutral-400 prose-p:my-1 prose-a:text-cyan-400 prose-code:text-cyan-300 prose-code:bg-neutral-900 prose-code:px-1">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{comment.content}</ReactMarkdown>
        </div>

        {hasTranslation && (
          <div className="mt-2 border border-dashed border-cyan-800/40 p-2 bg-cyan-950/10">
            <div className="prose prose-invert prose-sm max-w-none prose-p:text-neutral-400 prose-p:my-1 prose-a:text-cyan-400 prose-code:text-cyan-300 prose-code:bg-neutral-900 prose-code:px-1">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{translations[comment.id]}</ReactMarkdown>
            </div>
          </div>
        )}

        <div className="flex items-center gap-3 mt-1.5 font-mono text-[10px] text-neutral-700">
          <button onClick={() => handleVote(1)} className={`flex items-center gap-0.5 transition-colors ${uv === 1 ? "text-cyan-400" : "hover:text-cyan-400"}`}>
            <ChevronUp size={11} />
          </button>
          <span className="tabular-nums">{comment.vote_score}</span>
          <button onClick={() => handleVote(-1)} className={`flex items-center gap-0.5 transition-colors ${uv === -1 ? "text-red-400" : "hover:text-red-400"}`}>
            <ChevronDown size={11} />
          </button>
          {user && (
            <button onClick={() => onReply(comment.id)} className="hover:text-white uppercase tracking-wider transition-colors">
              {t("forum.reply")}
            </button>
          )}
          <button
            onClick={() => onTranslate(comment.id)}
            disabled={isTranslating}
            className="flex items-center gap-0.5 hover:text-cyan-400 transition-colors disabled:opacity-40"
          >
            <Languages size={10} />
            <span className="uppercase tracking-wider">
              {isTranslating ? t("forum.translating") : hasTranslation ? t("forum.showOriginal") : t("forum.translate")}
            </span>
          </button>
          {voteError && <span className="text-red-400 text-[8px]">{voteError}</span>}
        </div>
      </div>

      {comment.children?.map((child) => (
        <CommentTree
          key={child.id}
          comment={child}
          depth={depth + 1}
          onReply={onReply}
          user={user}
          onScoreChange={onScoreChange}
          translations={translations}
          translating={translating}
          onTranslate={onTranslate}
        />
      ))}
    </div>
  );
}
