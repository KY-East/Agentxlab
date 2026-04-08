from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class DisciplineBase(BaseModel):
    name_en: str
    name_zh: str | None = None
    parent_id: int | None = None
    depth: int = 0


class DisciplineOut(DisciplineBase):
    id: int
    level: str | None = None
    openalex_id: str | None = None
    works_count: int | None = None
    children: list[DisciplineOut] = []

    model_config = {"from_attributes": True}


class ScholarBrief(BaseModel):
    id: int
    name: str
    era: str | None = None

    model_config = {"from_attributes": True}


class ScholarOut(ScholarBrief):
    bio: str | None = None
    contribution: str | None = None
    affiliation: str | None = None
    works_count: int | None = None
    cited_by_count: int | None = None
    disciplines: list[DisciplineBrief] = []

    model_config = {"from_attributes": True}


class DisciplineCreate(BaseModel):
    name_en: str
    name_zh: str | None = None
    parent_id: int | None = None
    created_by: int | None = None


class DisciplineBrief(BaseModel):
    id: int
    name_en: str
    name_zh: str | None = None

    model_config = {"from_attributes": True}


class PaperBrief(BaseModel):
    id: int
    title: str
    year: int | None = None
    paper_type: str = "classic"

    model_config = {"from_attributes": True}


class PaperOut(PaperBrief):
    doi_or_url: str | None = None
    abstract: str | None = None
    source: str | None = None
    openalex_id: str | None = None
    doi: str | None = None
    citation_count: int | None = None
    authors: list[ScholarBrief] = []

    model_config = {"from_attributes": True}


class IntersectionBrief(BaseModel):
    id: int
    title: str
    status: str

    model_config = {"from_attributes": True}


class IntersectionOut(IntersectionBrief):
    core_tension: str | None = None
    classic_dialogue: str | None = None
    frontier_progress: str | None = None
    open_questions: str | None = None
    disciplines: list[DisciplineBrief] = []
    scholars: list[ScholarBrief] = []
    papers: list[PaperBrief] = []
    hypotheses: list[HypothesisOut] = []

    model_config = {"from_attributes": True}


class HypothesisOut(BaseModel):
    id: int
    model_name: str
    hypothesis_text: str
    created_at: datetime

    model_config = {"from_attributes": True}


class HypothesisRequest(BaseModel):
    discipline_ids: list[int]
    model: str | None = None
    language: str = "zh"


class ChatHypothesisRequest(BaseModel):
    intersection_id: int
    message: str
    history: list[dict] = []
    language: str = "zh"


class ChatHypothesisResponse(BaseModel):
    reply: str
    hypothesis: str | None = None
    suggestions: list[str] = []


class EdgeChatRequest(BaseModel):
    subfield_a_id: int
    subfield_b_id: int
    message: str
    history: list[dict] = []
    language: str = "zh"


class CanvasChatRequest(BaseModel):
    discipline_ids: list[int]
    message: str
    history: list[dict] = []
    language: str = "zh"


class IntersectionQuery(BaseModel):
    discipline_ids: list[int]


class GraphNode(BaseModel):
    id: int
    name_en: str
    name_zh: str | None = None
    depth: int
    parent_id: int | None = None
    root_id: int | None = None


class GraphEdge(BaseModel):
    source: int
    target: int
    intersection_id: int | None = None
    title: str
    status: str
    weight: int = 0
    paper_count: int = 0
    core_tension: str | None = None


class GraphData(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class TopicCrossPair(BaseModel):
    topic_a_id: int
    topic_a_name: str
    topic_b_id: int
    topic_b_name: str
    shared_papers: int


class EdgeDetail(BaseModel):
    subfield_a_id: int
    subfield_a_name: str
    subfield_b_id: int
    subfield_b_name: str
    total_papers: int
    topic_pairs: list[TopicCrossPair]


# ── Debate schemas ──


class DebateCreate(BaseModel):
    discipline_ids: list[int]
    mode: str = "free"
    proposition: str | None = None
    intersection_id: int | None = None
    language: str = "zh"
    discipline_weights: dict[int, int] | None = None


class AgentOut(BaseModel):
    id: int
    agent_name: str
    discipline_id: int | None = None
    persona: str
    rank: str = "professor"
    weight: int = 50
    stance: str | None = None
    sort_order: int

    model_config = {"from_attributes": True}


class MessageOut(BaseModel):
    id: int
    agent_id: int | None = None
    role: str
    content: str
    round_number: int
    created_at: datetime

    model_config = {"from_attributes": True}


class DebateBrief(BaseModel):
    id: int
    title: str
    mode: str
    status: str
    language: str = "zh"
    created_at: datetime

    model_config = {"from_attributes": True}


class DebateSummary(BaseModel):
    consensus: str | None = None
    disagreements: str | None = None
    open_questions: str | None = None
    directions: str | None = None


class DebateOut(DebateBrief):
    proposition: str | None = None
    intersection_id: int | None = None
    disciplines: list[DisciplineBrief] = []
    agents: list[AgentOut] = []
    messages: list[MessageOut] = []
    summary_consensus: str | None = None
    summary_disagreements: str | None = None
    summary_open_questions: str | None = None
    summary_directions: str | None = None

    model_config = {"from_attributes": True}


class ModeSuggestion(BaseModel):
    mode: str
    reason_en: str
    reason_zh: str
    suggested_proposition: str | None = None


class SuggestModeRequest(BaseModel):
    discipline_names: list[str]


# ── Discovery schemas ──


class DiscoverRequest(BaseModel):
    question: str


class MatchedDiscipline(BaseModel):
    discipline_id: int
    name_en: str | None = None
    name_zh: str | None = None
    relevance: float = 0.0
    reason_en: str = ""
    reason_zh: str = ""
    works_count: int | None = None


class ComboDiscipline(BaseModel):
    id: int
    name_en: str
    name_zh: str | None = None


class RecommendedCombo(BaseModel):
    discipline_ids: list[int]
    disciplines: list[ComboDiscipline] = []
    explanation_en: str = ""
    explanation_zh: str = ""
    direction_en: str = ""
    direction_zh: str = ""
    existing_intersection_id: int | None = None
    intersection_title: str | None = None
    is_gap: bool = True


class DiscoveryResult(BaseModel):
    question: str
    matched_disciplines: list[MatchedDiscipline] = []
    recommended_combos: list[RecommendedCombo] = []


# ── Forum Schemas ────────────────────────────────────────────────

class ForumAuthor(BaseModel):
    id: int
    display_name: str
    avatar_url: str | None = None
    points: int


class ForumPostCreate(BaseModel):
    title: str
    content: str
    post_type: str = "discussion"
    discipline_tags: list[str] | None = None
    parent_post_id: int | None = None


class ForumPostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    status: str | None = None
    is_pinned: bool | None = None


class ForumPostOut(BaseModel):
    id: int
    user_id: int | None = None
    author: ForumAuthor | None = None
    title: str
    content: str
    zone: str
    post_type: str
    status: str
    debate_id: int | None = None
    spark_id: int | None = None
    parent_post_id: int | None = None
    discipline_tags: list[str] | None = None
    vote_score: int
    comment_count: int
    is_pinned: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ForumCommentCreate(BaseModel):
    content: str
    parent_id: int | None = None
    comment_type: str = "normal"


class ForumCommentOut(BaseModel):
    id: int
    post_id: int
    user_id: int
    author: ForumAuthor | None = None
    parent_id: int | None = None
    content: str
    vote_score: int
    comment_type: str
    created_at: datetime
    children: list["ForumCommentOut"] = []

    model_config = {"from_attributes": True}


class VoteRequest(BaseModel):
    vote_type: int
    target_type: str
    target_id: int


class VoteResponse(BaseModel):
    new_score: int
    user_vote: int | None = None


# ── Points Schemas ───────────────────────────────────────────────

class PointLogOut(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    user_id: int
    action: str
    points: int
    reference_type: str | None = None
    reference_id: int | None = None
    created_at: datetime


class LeaderboardEntry(BaseModel):
    user_id: int
    display_name: str
    avatar_url: str | None = None
    points: int


# ── Spark Schemas ────────────────────────────────────────────────

class SparkOut(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    debate_id: int
    message_id: int | None = None
    agent_id: int | None = None
    source_discipline_id: int | None = None
    target_discipline_id: int | None = None
    content: str
    novelty_type: str = "analogy"
    novelty_score: float = 0.0
    reasoning: str | None = None
    verification_status: str = "unverified"


class ExperimentMetaOut(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    debate_id: int
    discipline_count: int = 0
    agent_count: int = 0
    round_count: int = 0
    message_count: int = 0
    persona_distribution: str | None = None
    rank_distribution: str | None = None
    weight_distribution: str | None = None
    discipline_names: str | None = None
    mode: str = "free"
    spark_count: int = 0
    avg_novelty_score: float = 0.0
    spark_type_distribution: str | None = None


# ── Paper Draft Schemas ──────────────────────────────────────────

class SectionOut(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    sort_order: int = 0
    heading: str
    summary: str | None = None
    writing_instruction: str | None = None
    content: str | None = None
    status: str = "pending"
    version: int = 1


class SectionUpdate(BaseModel):
    id: int | None = None
    heading: str | None = None
    summary: str | None = None
    writing_instruction: str | None = None
    sort_order: int | None = None


class DraftCreate(BaseModel):
    debate_id: int
    direction: str


class DraftUpdate(BaseModel):
    title: str | None = None
    sections: list[SectionUpdate] | None = None


class DraftOut(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    title: str
    debate_id: int
    direction: str | None = None
    status: str = "outline"
    sections: list[SectionOut] = []


class DraftBrief(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    title: str
    direction: str | None = None
    status: str = "outline"


# Rebuild forward refs
ScholarOut.model_rebuild()
IntersectionOut.model_rebuild()
DebateOut.model_rebuild()
ForumCommentOut.model_rebuild()