import { useState, useEffect, useCallback } from "react";
import { useTranslation } from "react-i18next";
import { useParams, useNavigate, Link } from "react-router-dom";
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
} from "lucide-react";

const STATUS_COLORS: Record<string, string> = {
  open: "text-neutral-500",
  theory_ready: "text-blue-400",
  experimenting: "text-yellow-500",
  verified: "text-green-400",
  falsified: "text-red-500",
};

export default function ForumPostDetail() {
  const { t, i18n } = useTranslation();
  const { postId } = useParams<{ postId: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [post, setPost] = useState<ForumPost | null>(null);
  const [comments, setComments] = useState<ForumCommentType[]>([]);
  const [loading, setLoading] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [commentText, setCommentText] = useState("");
  const [replyTo, setReplyTo] = useState<number | null>(null);
  const [commentType, setCommentType] = useState<string>("normal");
  const [sending, setSending] = useState(false);
  const [commentError, setCommentError] = useState<string | null>(null);

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
        setFetchError(msg || "Failed to load");
      }
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleVote = async (voteType: 1 | -1) => {
    if (!user || !post) return;
    try {
      const res = await api.forumVote({
        target_type: "post",
        target_id: post.id,
        vote_type: voteType,
      });
      setPost((p) => (p ? { ...p, vote_score: res.new_score } : p));
    } catch {}
  };

  const handleComment = async () => {
    if (!commentText.trim() || !user) return;
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
      const c = await api.getForumComments(id);
      setComments(c);
      setPost((p) => (p ? { ...p, comment_count: p.comment_count + 1 } : p));
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setCommentError(msg || "Comment failed");
    } finally {
      setSending(false);
    }
  };

  if (loading) {
    return (
      <div className="p-8">
        <span className="font-mono text-xs text-neutral-600 animate-blink">[LOADING...]</span>
      </div>
    );
  }
  if (fetchError) {
    return (
      <div className="p-8 space-y-3">
        <p className="font-mono text-xs text-red-500">{fetchError}</p>
        <button
          onClick={fetchData}
          className="font-mono text-xs text-cyan-400 hover:text-white underline transition-colors"
        >
          {t("common.retry")}
        </button>
      </div>
    );
  }
  if (!post) {
    return <div className="p-8 font-mono text-xs text-neutral-600">Post not found</div>;
  }

  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-3xl mx-auto px-6 py-6 space-y-6">
        {/* Back */}
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-1 font-mono text-[10px] text-neutral-600 hover:text-white uppercase tracking-wider transition-colors"
        >
          <ArrowLeft size={10} /> {t("common.back")}
        </button>

        {/* Post header */}
        <div className="flex gap-4">
          {/* Vote column */}
          <div className="flex flex-col items-center gap-0.5 pt-1 shrink-0">
            <button onClick={() => handleVote(1)} className="text-neutral-600 hover:text-cyan-400 transition-colors">
              <ChevronUp size={18} />
            </button>
            <span className="font-mono text-base font-bold text-neutral-300">{post.vote_score}</span>
            <button onClick={() => handleVote(-1)} className="text-neutral-600 hover:text-red-400 transition-colors">
              <ChevronDown size={18} />
            </button>
          </div>

          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap mb-2">
              <span
                className={`font-mono text-[9px] uppercase tracking-wider ${STATUS_COLORS[post.status] || "text-neutral-500"}`}
              >
                {post.status}
              </span>
              {post.zone === "ai_generated" && (
                <span className="font-mono text-[9px] uppercase tracking-wider text-cyan-400">AI</span>
              )}
              <span className="font-mono text-[9px] text-neutral-600 uppercase tracking-wider">{post.post_type}</span>
              {post.debate_id && (
                <Link
                  to={`/debate/${post.debate_id}`}
                  className="font-mono text-[9px] text-cyan-400 hover:text-white underline transition-colors"
                >
                  {t("forum.viewDebate", { id: post.debate_id })}
                </Link>
              )}
            </div>

            <h1 className="text-lg font-bold text-white">{post.title}</h1>

            <div className="flex items-center gap-3 mt-2 font-mono text-[10px] text-neutral-600">
              {post.author ? (
                <span className="flex items-center gap-1">
                  {post.author.avatar_url && (
                    <img src={post.author.avatar_url} alt="" className="w-3.5 h-3.5 rounded-sm" />
                  )}
                  {post.author.display_name}
                </span>
              ) : (
                <span className="text-cyan-400/60">Agent X Lab</span>
              )}
              <span>
                {new Date(post.created_at).toLocaleString(i18n.language === "zh" ? "zh-CN" : "en-US")}
              </span>
              {post.discipline_tags && (
                <span className="text-neutral-700">{post.discipline_tags.join(" / ")}</span>
              )}
            </div>
          </div>
        </div>

        {/* Post body */}
        <div className="border-l-2 border-neutral-800 pl-4 py-2">
          <div className="text-sm text-neutral-300 leading-relaxed whitespace-pre-wrap">
            {post.content}
          </div>
        </div>

        {/* Comment box */}
        {user && (
          <div className="border-2 border-neutral-800 p-4 space-y-3">
            {replyTo && (
              <div className="font-mono text-[10px] text-neutral-500 flex items-center gap-2">
                Replying to #{replyTo}
                <button onClick={() => setReplyTo(null)} className="text-red-500 hover:text-red-400 transition-colors">
                  CANCEL
                </button>
              </div>
            )}

            <div className="flex items-center gap-2">
              {post.zone === "ai_generated" && (
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
                placeholder={
                  commentType === "claim_experiment"
                    ? t("forum.describeVerifyPlaceholder")
                    : t("forum.commentPlaceholder")
                }
                rows={3}
                className="flex-1 bg-transparent border border-neutral-800 px-3 py-2 text-sm text-neutral-300 placeholder-neutral-700 resize-none focus:outline-none focus:border-cyan-400"
              />
              <button
                onClick={handleComment}
                disabled={sending || !commentText.trim()}
                className="self-end px-3 py-2 bg-cyan-400 text-black hover:bg-cyan-300 disabled:opacity-50 transition-colors"
              >
                {commentType === "claim_experiment" ? (
                  <FlaskConical size={14} />
                ) : (
                  <Send size={14} />
                )}
              </button>
            </div>
            {commentError && (
              <p className="font-mono text-[10px] text-red-500">{commentError}</p>
            )}
          </div>
        )}

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
                  onReply={(id) => setReplyTo(id)}
                  user={user}
                  onScoreChange={(cid, score) => {
                    setComments((prev) => updateScore(prev, cid, score));
                  }}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function updateScore(
  comments: ForumCommentType[],
  targetId: number,
  newScore: number,
): ForumCommentType[] {
  return comments.map((c) => {
    if (c.id === targetId) return { ...c, vote_score: newScore };
    if (c.children?.length)
      return { ...c, children: updateScore(c.children, targetId, newScore) };
    return c;
  });
}

function CommentTree({
  comment,
  depth,
  onReply,
  user,
  onScoreChange,
}: {
  comment: ForumCommentType;
  depth: number;
  onReply: (id: number) => void;
  user: { id: number } | null;
  onScoreChange: (commentId: number, newScore: number) => void;
}) {
  const { t, i18n } = useTranslation();
  const handleVote = async (voteType: 1 | -1) => {
    if (!user) return;
    try {
      const res = await api.forumVote({
        target_type: "comment",
        target_id: comment.id,
        vote_type: voteType,
      });
      onScoreChange(comment.id, res.new_score);
    } catch {}
  };

  return (
    <div className={`${depth > 0 ? "ml-5 border-l border-neutral-800 pl-3" : ""}`}>
      <div className="py-2.5">
        <div className="flex items-center gap-2 font-mono text-[10px] text-neutral-600 mb-1">
          {comment.author && (
            <span className="flex items-center gap-1">
              {comment.author.avatar_url && (
                <img src={comment.author.avatar_url} alt="" className="w-3 h-3 rounded-sm" />
              )}
              <span className="text-neutral-400">{comment.author.display_name}</span>
            </span>
          )}
          <span>
            {new Date(comment.created_at).toLocaleString(i18n.language === "zh" ? "zh-CN" : "en-US")}
          </span>
          {comment.comment_type === "claim_experiment" && (
            <span className="uppercase tracking-wider text-yellow-500">CLAIM</span>
          )}
          {comment.comment_type === "submit_result" && (
            <span className="uppercase tracking-wider text-green-400">RESULT</span>
          )}
        </div>

        <p className="text-sm text-neutral-400 whitespace-pre-wrap">{comment.content}</p>

        <div className="flex items-center gap-3 mt-1.5 font-mono text-[10px] text-neutral-700">
          <button onClick={() => handleVote(1)} className="hover:text-cyan-400 flex items-center gap-0.5 transition-colors">
            <ChevronUp size={11} /> {comment.vote_score}
          </button>
          {user && (
            <button onClick={() => onReply(comment.id)} className="hover:text-white uppercase tracking-wider transition-colors">
              {t("forum.reply")}
            </button>
          )}
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
        />
      ))}
    </div>
  );
}
