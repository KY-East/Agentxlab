const API_BASE = import.meta.env.VITE_API_BASE ?? "";
const TOKEN_KEY = "axl_token";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const token = localStorage.getItem(TOKEN_KEY);
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init?.headers as Record<string, string>),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, { ...init, headers });
  if (!res.ok) {
    const text = await res.text();
    if (res.status === 429) {
      window.dispatchEvent(new CustomEvent("axl:quota-exceeded"));
    }
    throw new Error(`API error ${res.status}: ${text}`);
  }
  return res.json();
}

export const api = {
  getDisciplines: (userId?: number) =>
    request<import("../types").Discipline[]>(
      `/api/disciplines${userId ? `?user_id=${userId}` : ""}`
    ),

  createDiscipline: (data: {
    name_en: string;
    name_zh?: string;
    parent_id?: number;
    created_by: number;
  }) =>
    request<import("../types").Discipline>("/api/disciplines", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  deleteDiscipline: (id: number) =>
    request<void>(`/api/disciplines/${id}`, { method: "DELETE" }),

  getScholarsByDiscipline: (id: number) =>
    request<import("../types").ScholarBrief[]>(`/api/disciplines/${id}/scholars`),

  getIntersections: (status?: string) =>
    request<import("../types").IntersectionBrief[]>(
      `/api/intersections${status ? `?status=${status}` : ""}`
    ),

  getIntersection: (id: number) =>
    request<import("../types").Intersection>(`/api/intersections/${id}`),

  queryIntersections: (disciplineIds: number[]) =>
    request<import("../types").Intersection[]>("/api/intersections/query", {
      method: "POST",
      body: JSON.stringify({ discipline_ids: disciplineIds }),
    }),

  getGraph: (ids?: number[]) =>
    request<import("../types").GraphData>(
      ids && ids.length > 0 ? `/api/graph?ids=${ids.join(",")}` : "/api/graph"
    ),

  getEdgeDetail: (a: number, b: number) =>
    request<import("../types").EdgeDetail>(`/api/graph/edge-detail?a=${a}&b=${b}`),

  getScholar: (id: number) =>
    request<import("../types").Scholar>(`/api/scholars/${id}`),

  getPaper: (id: number) =>
    request<import("../types").Paper>(`/api/papers/${id}`),

  generateHypothesis: (disciplineIds: number[], model?: string, language?: string) =>
    request<import("../types").Hypothesis>("/api/ai/hypothesis", {
      method: "POST",
      body: JSON.stringify({ discipline_ids: disciplineIds, model, language: language || "zh" }),
    }),

  chatHypothesis: (payload: {
    intersection_id: number;
    message: string;
    history?: { role: string; content: string }[];
    language?: string;
  }) =>
    request<import("../types").ChatHypothesisResponse>("/api/ai/chat-hypothesis", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  edgeChat: (payload: {
    subfield_a_id: number;
    subfield_b_id: number;
    message: string;
    history?: { role: string; content: string }[];
    language?: string;
  }) =>
    request<import("../types").ChatHypothesisResponse>("/api/ai/edge-chat", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  canvasChat: (payload: {
    discipline_ids: number[];
    message: string;
    history?: { role: string; content: string }[];
    language?: string;
  }) =>
    request<import("../types").ChatHypothesisResponse>("/api/ai/canvas-chat", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  // ── Debate API ──

  createDebate: (params: {
    discipline_ids: number[];
    mode: string;
    proposition?: string;
    intersection_id?: number;
    discipline_weights?: Record<number, number>;
    language?: string;
  }) =>
    request<import("../types").Debate>("/api/debates", {
      method: "POST",
      body: JSON.stringify(params),
    }),

  getDebates: (params?: { status?: string; created_by?: number }) => {
    const qs = new URLSearchParams();
    if (params?.status) qs.set("status", params.status);
    if (params?.created_by != null) qs.set("created_by", String(params.created_by));
    const q = qs.toString();
    return request<import("../types").DebateBrief[]>(`/api/debates${q ? `?${q}` : ""}`);
  },

  getDebate: (id: number) =>
    request<import("../types").Debate>(`/api/debates/${id}`),

  runRound: (debateId: number) =>
    request<import("../types").DebateMessage[]>(
      `/api/debates/${debateId}/rounds`,
      { method: "POST" }
    ),

  runRoundStream: (debateId: number) => {
    const token = localStorage.getItem(TOKEN_KEY);
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;
    return fetch(`${API_BASE}/api/debates/${debateId}/rounds/stream`, {
      method: "POST",
      headers,
    });
  },

  summarizeDebate: (debateId: number) =>
    request<import("../types").Debate>(
      `/api/debates/${debateId}/summarize`,
      { method: "POST" }
    ),

  suggestMode: (disciplineNames: string[]) =>
    request<import("../types").ModeSuggestion>("/api/debates/suggest-mode", {
      method: "POST",
      body: JSON.stringify({ discipline_names: disciplineNames }),
    }),

  shareDebateToForum: (debateId: number) =>
    request<{ post_id: number; title: string }>(`/api/debates/${debateId}/share-to-forum`, {
      method: "POST",
    }),

  requestExperiment: (debateId: number, sparkId: number) =>
    request<{ post_id: number; title: string; already_exists: boolean }>(
      `/api/debates/${debateId}/sparks/${sparkId}/request-experiment`,
      { method: "POST" }
    ),

  // ── Discovery API ──

  discover: (question: string) =>
    request<import("../types").DiscoveryResult>("/api/discover", {
      method: "POST",
      body: JSON.stringify({ question }),
    }),

  // ── Paper Draft API ──

  createDraft: (debateId: number, direction: string) =>
    request<import("../types").DraftOut>("/api/papers/drafts", {
      method: "POST",
      body: JSON.stringify({ debate_id: debateId, direction }),
    }),

  listDrafts: (debateId?: number) =>
    request<import("../types").DraftBrief[]>(
      `/api/papers/drafts${debateId != null ? `?debate_id=${debateId}` : ""}`
    ),

  getDraft: (draftId: number) =>
    request<import("../types").DraftOut>(`/api/papers/drafts/${draftId}`),

  updateDraft: (draftId: number, payload: import("../types").DraftUpdatePayload) =>
    request<import("../types").DraftOut>(`/api/papers/drafts/${draftId}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),

  generateSection: (draftId: number, sectionId: number) =>
    request<import("../types").PaperSectionOut>(
      `/api/papers/drafts/${draftId}/sections/${sectionId}/generate`,
      { method: "POST" }
    ),

  exportDraft: (draftId: number) => {
    const token = localStorage.getItem(TOKEN_KEY);
    const headers: Record<string, string> = {};
    if (token) headers["Authorization"] = `Bearer ${token}`;
    return fetch(`${API_BASE}/api/papers/drafts/${draftId}/export`, { headers }).then((r) => {
      if (!r.ok) throw new Error(`Export failed: ${r.status}`);
      return r.text();
    });
  },

  suggestDirections: (debateId: number) =>
    request<{ directions: { title: string; description: string; estimated_sections: number }[] }>(
      "/api/papers/drafts/suggest-directions",
      { method: "POST", body: JSON.stringify({ debate_id: debateId }) }
    ),

  chatRefineOutline: (payload: {
    debate_id: number;
    current_title: string;
    current_sections: { heading: string; summary: string }[];
    message: string;
  }) =>
    request<{ title: string; sections: { heading: string; summary: string }[]; reply: string }>(
      "/api/papers/drafts/chat-refine",
      { method: "POST", body: JSON.stringify(payload) }
    ),

  generateAllSections: (draftId: number) => {
    const token = localStorage.getItem(TOKEN_KEY);
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;
    return fetch(`${API_BASE}/api/papers/drafts/${draftId}/generate-all`, {
      method: "POST",
      headers,
    });
  },

  // ── Spark API ──

  listSparks: (params?: {
    debate_id?: number;
    discipline_id?: number;
    min_score?: number;
    novelty_type?: string;
    limit?: number;
    offset?: number;
  }) => {
    const qs = new URLSearchParams();
    if (params?.debate_id != null) qs.set("debate_id", String(params.debate_id));
    if (params?.discipline_id != null) qs.set("discipline_id", String(params.discipline_id));
    if (params?.min_score != null) qs.set("min_score", String(params.min_score));
    if (params?.novelty_type) qs.set("novelty_type", params.novelty_type);
    if (params?.limit != null) qs.set("limit", String(params.limit));
    if (params?.offset != null) qs.set("offset", String(params.offset));
    const q = qs.toString();
    return request<import("../types").Spark[]>(`/api/sparks${q ? `?${q}` : ""}`);
  },

  getSparkStats: (debateId?: number) =>
    request<import("../types").SparkStats>(
      `/api/sparks/stats${debateId != null ? `?debate_id=${debateId}` : ""}`
    ),

  getExperimentMeta: (debateId: number) =>
    request<import("../types").ExperimentMeta>(
      `/api/sparks/experiments/${debateId}`
    ),

  listExperiments: (limit?: number) =>
    request<import("../types").ExperimentMeta[]>(
      `/api/sparks/experiments${limit ? `?limit=${limit}` : ""}`
    ),

  // ── Forum API ──

  listForumPosts: (params?: {
    zone?: string;
    post_type?: string;
    status?: string;
    discipline_tag?: string;
    user_id?: number;
    debate_id?: number;
    sort?: string;
    limit?: number;
    offset?: number;
  }) => {
    const qs = new URLSearchParams();
    if (params?.zone) qs.set("zone", params.zone);
    if (params?.post_type) qs.set("post_type", params.post_type);
    if (params?.status) qs.set("status", params.status);
    if (params?.discipline_tag) qs.set("discipline_tag", params.discipline_tag);
    if (params?.user_id != null) qs.set("user_id", String(params.user_id));
    if (params?.debate_id != null) qs.set("debate_id", String(params.debate_id));
    if (params?.sort) qs.set("sort", params.sort);
    if (params?.limit != null) qs.set("limit", String(params.limit));
    if (params?.offset != null) qs.set("offset", String(params.offset));
    const q = qs.toString();
    return request<import("../types").ForumPost[]>(`/api/forum/posts${q ? `?${q}` : ""}`);
  },

  getForumPost: (id: number) =>
    request<import("../types").ForumPost>(`/api/forum/posts/${id}`),

  getForumStats: () =>
    request<{ total_posts: number; ai_posts: number; community_posts: number; experiment_posts: number; verified_posts: number; total_comments: number }>("/api/forum/stats"),

  getHotTags: (limit?: number) =>
    request<{ tag: string; count: number }[]>(`/api/forum/hot-tags${limit ? `?limit=${limit}` : ""}`),

  createForumPost: (body: { title: string; content: string; post_type?: string; discipline_tags?: string[]; parent_post_id?: number }) =>
    request<import("../types").ForumPost>("/api/forum/posts", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  updateForumPost: (id: number, body: { title?: string; content?: string; status?: string; is_pinned?: boolean }) =>
    request<import("../types").ForumPost>(`/api/forum/posts/${id}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),

  deleteForumPost: (id: number) =>
    request<{ ok: boolean }>(`/api/forum/posts/${id}`, { method: "DELETE" }),

  updateMe: (body: { display_name?: string; avatar_url?: string }) =>
    request<{ id: number; email: string; display_name: string; avatar_url: string | null; did_address: string | null; points: number; role: string }>("/api/auth/me", {
      method: "PATCH",
      body: JSON.stringify(body),
    }),

  getForumComments: (postId: number) =>
    request<import("../types").ForumComment[]>(`/api/forum/posts/${postId}/comments`),

  createForumComment: (postId: number, body: { content: string; parent_id?: number; comment_type?: string; result_verdict?: string }) =>
    request<import("../types").ForumComment>(`/api/forum/posts/${postId}/comments`, {
      method: "POST",
      body: JSON.stringify(body),
    }),

  forumVote: (body: { target_type: string; target_id: number; vote_type: number }) =>
    request<import("../types").VoteResponse>("/api/forum/vote", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  // ── Points API ──

  getPointLog: (limit?: number, offset?: number) => {
    const qs = new URLSearchParams();
    if (limit != null) qs.set("limit", String(limit));
    if (offset != null) qs.set("offset", String(offset));
    const q = qs.toString();
    return request<import("../types").PointLogEntry[]>(`/api/points/log${q ? `?${q}` : ""}`);
  },

  getLeaderboard: (limit?: number) =>
    request<import("../types").LeaderboardEntry[]>(
      `/api/points/leaderboard${limit ? `?limit=${limit}` : ""}`
    ),

  // ── Translation API ──

  translateContent: (body: {
    content_type: "post" | "comment";
    content_id: number;
    fields: string[];
    target_lang: string;
  }) =>
    request<{ translations: Record<string, string> }>("/api/forum/translate", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  // ── Subscription API ──

  getPlans: () =>
    request<import("../types").PlanInfo[]>("/api/subscription/plans"),

  getMySubscription: () =>
    request<import("../types").SubscriptionInfo>("/api/subscription/me"),

  updatePreferredModel: (preferred_model: string) =>
    request<import("../types").SubscriptionInfo>("/api/subscription/model", {
      method: "PATCH",
      body: JSON.stringify({ preferred_model }),
    }),

  getUsage: () =>
    request<import("../types").UsageInfo>("/api/subscription/usage"),

  createStripeCheckout: (plan: string) =>
    request<{ checkout_url: string }>(`/api/payment/stripe/checkout?plan=${plan}`, {
      method: "POST",
    }),

  createStripePortal: () =>
    request<{ portal_url: string }>("/api/payment/stripe/portal", {
      method: "POST",
    }),

  requestCryptoPayment: (plan: string) =>
    request<{
      payment_id: number;
      wallet_address: string;
      network: string;
      amount_usd: number;
      memo: string;
      status: string;
    }>("/api/payment/crypto/request", {
      method: "POST",
      body: JSON.stringify({ plan }),
    }),

  submitCryptoTx: (paymentId: number, txHash: string) =>
    request<{ ok: boolean }>(`/api/payment/crypto/submit-tx?payment_id=${paymentId}&tx_hash=${encodeURIComponent(txHash)}`, {
      method: "POST",
    }),
};
