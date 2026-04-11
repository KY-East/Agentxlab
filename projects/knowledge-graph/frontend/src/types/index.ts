export interface DisciplineBrief {
  id: number;
  name_en: string;
  name_zh: string | null;
}

export interface Discipline extends DisciplineBrief {
  parent_id: number | null;
  depth: number;
  level: string | null;
  openalex_id: string | null;
  works_count: number | null;
  is_custom: boolean;
  created_by: number | null;
  children: Discipline[];
}

export interface ScholarBrief {
  id: number;
  name: string;
  era: string | null;
}

export interface Scholar extends ScholarBrief {
  bio: string | null;
  contribution: string | null;
  affiliation: string | null;
  works_count: number | null;
  cited_by_count: number | null;
  disciplines: DisciplineBrief[];
}

export interface PaperBrief {
  id: number;
  title: string;
  year: number | null;
  paper_type: "classic" | "frontier";
}

export interface Paper extends PaperBrief {
  doi_or_url: string | null;
  abstract: string | null;
  source: string | null;
  citation_count: number | null;
  authors: ScholarBrief[];
}

export interface Hypothesis {
  id: number;
  model_name: string;
  hypothesis_text: string;
  created_at: string;
}

export interface IntersectionBrief {
  id: number;
  title: string;
  status: "active" | "gap";
}

export interface Intersection extends IntersectionBrief {
  core_tension: string | null;
  classic_dialogue: string | null;
  frontier_progress: string | null;
  open_questions: string | null;
  disciplines: DisciplineBrief[];
  scholars: ScholarBrief[];
  papers: PaperBrief[];
  hypotheses: Hypothesis[];
}

export interface GraphNode {
  id: number;
  name_en: string;
  name_zh: string | null;
  depth: number;
  parent_id: number | null;
  root_id: number | null;
}

export interface GraphEdge {
  source: number;
  target: number;
  intersection_id: number | null;
  title: string;
  status: "active" | "gap" | "evidence";
  weight: number;
  paper_count: number;
  core_tension: string | null;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface D3Node extends GraphNode {
  x?: number;
  y?: number;
  fx?: number | null;
  fy?: number | null;
}

export interface D3Edge {
  source: D3Node;
  target: D3Node;
  intersection_id: number | null;
  title: string;
  status: "active" | "gap" | "evidence";
  weight: number;
  paper_count: number;
  core_tension: string | null;
}

export interface TopicCrossPair {
  topic_a_id: number;
  topic_a_name: string;
  topic_b_id: number;
  topic_b_name: string;
  shared_papers: number;
}

export interface EdgeDetail {
  subfield_a_id: number;
  subfield_a_name: string;
  subfield_b_id: number;
  subfield_b_name: string;
  total_papers: number;
  topic_pairs: TopicCrossPair[];
}

// ── Debate types ──

export interface DebateAgent {
  id: number;
  agent_name: string;
  discipline_id: number | null;
  persona: string;
  rank: "professor" | "associate" | "assistant";
  weight: number;
  stance: string | null;
  sort_order: number;
}

export interface DebateMessage {
  id: number;
  agent_id: number | null;
  role: "agent" | "system" | "user" | "summary";
  content: string;
  round_number: number;
  created_at: string;
}

export interface DebateBrief {
  id: number;
  title: string;
  mode: "free" | "debate";
  language: "zh" | "en";
  status: "active" | "summarizing" | "completed";
  created_at: string;
}

export interface Debate extends DebateBrief {
  proposition: string | null;
  intersection_id: number | null;
  disciplines: DisciplineBrief[];
  agents: DebateAgent[];
  messages: DebateMessage[];
  summary_consensus: string | null;
  summary_disagreements: string | null;
  summary_open_questions: string | null;
  summary_directions: string | null;
}

export interface ModeSuggestion {
  mode: "free" | "debate";
  reason_en: string;
  reason_zh: string;
  suggested_proposition: string | null;
}

// ── Discovery types ──

export interface MatchedDiscipline {
  discipline_id: number;
  name_en: string | null;
  name_zh: string | null;
  relevance: number;
  reason_en: string;
  reason_zh: string;
  works_count: number | null;
}

export interface ComboDiscipline {
  id: number;
  name_en: string;
  name_zh: string | null;
}

export interface RecommendedCombo {
  discipline_ids: number[];
  disciplines: ComboDiscipline[];
  explanation_en: string;
  explanation_zh: string;
  direction_en: string;
  direction_zh: string;
  existing_intersection_id: number | null;
  intersection_title: string | null;
  is_gap: boolean;
}

export interface DiscoveryResult {
  question: string;
  matched_disciplines: MatchedDiscipline[];
  recommended_combos: RecommendedCombo[];
}

// ── Paper Draft types ──

export interface PaperSectionOut {
  id: number;
  sort_order: number;
  heading: string;
  summary: string | null;
  writing_instruction: string | null;
  content: string | null;
  status: "pending" | "generating" | "completed";
  version: number;
}

export interface DraftBrief {
  id: number;
  title: string;
  debate_id: number;
  direction: string | null;
  status: "outline" | "writing" | "completed";
  created_at: string;
}

export interface DraftOut extends DraftBrief {
  sections: PaperSectionOut[];
  updated_at: string | null;
}

export interface SectionUpdate {
  id?: number;
  sort_order?: number;
  heading?: string;
  summary?: string;
  writing_instruction?: string;
}

export interface DraftUpdatePayload {
  title?: string;
  sections?: SectionUpdate[];
}

// ── User types ──

export interface UserBrief {
  id: number;
  display_name: string;
  avatar_url: string | null;
  points: number;
  role: string;
}

// ── Forum types ──

export interface ForumAuthor {
  id: number;
  display_name: string;
  avatar_url: string | null;
  points: number;
}

export interface ForumPost {
  id: number;
  user_id: number | null;
  author: ForumAuthor | null;
  title: string;
  content: string;
  zone: "ai_generated" | "community";
  post_type: string;
  status: string;
  debate_id: number | null;
  spark_id: number | null;
  parent_post_id: number | null;
  discipline_tags: string[] | null;
  vote_score: number;
  comment_count: number;
  is_pinned: boolean;
  created_at: string;
  updated_at: string | null;
}

export interface ForumComment {
  id: number;
  post_id: number;
  user_id: number;
  author: ForumAuthor | null;
  parent_id: number | null;
  content: string;
  vote_score: number;
  comment_type: string;
  created_at: string;
  children: ForumComment[];
}

export interface VoteResponse {
  new_score: number;
  user_vote: number | null;
}

export interface PointLogEntry {
  id: number;
  action: string;
  points: number;
  reference_type: string | null;
  reference_id: number | null;
  created_at: string;
}

export interface LeaderboardEntry {
  user_id: number;
  display_name: string;
  avatar_url: string | null;
  points: number;
}

// ── Spark types ──

export interface Spark {
  id: number;
  debate_id: number;
  message_id: number | null;
  agent_id: number | null;
  source_discipline_id: number | null;
  target_discipline_id: number | null;
  content: string;
  novelty_type: "analogy" | "transfer" | "fusion" | "inversion";
  novelty_score: number;
  reasoning: string | null;
  verification_status: string;
  created_at: string;
}

export interface SparkStats {
  total: number;
  avg_score: number;
  by_type: Record<string, number>;
  by_verification: Record<string, number>;
}

export interface ExperimentMeta {
  id: number;
  debate_id: number;
  discipline_count: number;
  agent_count: number;
  round_count: number;
  message_count: number;
  persona_distribution: string | null;
  rank_distribution: string | null;
  weight_distribution: string | null;
  discipline_names: string | null;
  mode: string;
  spark_count: number;
  avg_novelty_score: number;
  spark_type_distribution: string | null;
  created_at: string;
}

export interface ChatHypothesisResponse {
  reply: string;
  hypothesis: string | null;
  suggestions: string[];
}

// ── Subscription ──

export interface PlanInfo {
  name: string;
  label_en: string;
  label_zh: string;
  monthly_tokens: number;
  allowed_models: string[];
  price_monthly_cents: number;
  price_once_cents: number;
}

export interface SubscriptionInfo {
  plan: string;
  status: string;
  monthly_token_limit: number;
  tokens_used_this_month: number;
  quota_reset_at: string | null;
  allowed_models: string[];
  preferred_model: string | null;
  stripe_customer_id: string | null;
}

export interface UsageInfo {
  tokens_used: number;
  tokens_limit: number;
  quota_reset_at: string | null;
  payments: {
    id: number;
    amount_cents: number;
    currency: string;
    payment_method: string;
    plan: string;
    status: string;
    created_at: string;
  }[];
}
