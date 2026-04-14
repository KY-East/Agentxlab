"""
Zep Cloud integration (SDK v3) — push knowledge into Zep Graph for RAG.

All writes carry structured metadata: origin, evidence_ref, memory_type,
source, confidence, verification. Retrieval applies metadata filters and
origin-based re-ranking (external > generated).
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from zep_cloud.client import Zep
from zep_cloud.types import (
    EpisodeMetadataFilter,
    MetadataFilterGroup,
    SearchFilters,
)

from app.config import settings

logger = logging.getLogger(__name__)

_client: Zep | None = None
GRAPH_ID = "agent-x-lab"
USER_SYSTEM = "system-knowledge"

ORIGIN_WEIGHT = {"external": 1.2, "generated": 0.9}


def get_zep_client() -> Zep:
    global _client
    if _client is None:
        if not settings.zep_api_key:
            raise RuntimeError("ZEP_API_KEY not configured")
        _client = Zep(api_key=settings.zep_api_key)
    return _client


def _ensure_user(user_id: str = USER_SYSTEM) -> None:
    client = get_zep_client()
    try:
        client.user.get(user_id)
    except Exception:
        client.user.add(user_id=user_id)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _base_metadata(
    *,
    memory_type: str,
    origin: str,
    source: str = "axl",
    confidence: str = "medium",
    verification: str = "unverified",
    evidence_ref: str | None = None,
    source_id: str | None = None,
) -> dict[str, Any]:
    """Build the standard metadata dict (max 10 keys per Zep limit)."""
    return {
        "memory_type": memory_type,
        "origin": origin,
        "source": source,
        "source_id": source_id or "",
        "confidence": confidence,
        "verification": verification,
        "evidence_ref": evidence_ref or "",
        "created_at": _now_iso(),
    }


# ---------------------------------------------------------------------------
# Writers
# ---------------------------------------------------------------------------

def push_discipline_knowledge(
    discipline_name: str,
    description: str,
    related_subfields: list[str] | None = None,
    *,
    openalex_id: str | None = None,
) -> None:
    client = get_zep_client()
    _ensure_user()

    content = f"Academic discipline: {discipline_name}."
    if description:
        content += f" Description: {description}."
    if related_subfields:
        content += f" Related subfields: {', '.join(related_subfields)}."

    meta = _base_metadata(
        memory_type="insight",
        origin="external",
        confidence="high",
        verification="peer_reviewed",
        evidence_ref=f"openalex_{openalex_id}" if openalex_id else "",
        source_id=f"discipline_{discipline_name}",
    )

    client.graph.add(
        data=content,
        type="text",
        user_id=USER_SYSTEM,
        graph_id=GRAPH_ID,
        metadata=meta,
    )
    logger.info("Pushed discipline knowledge: %s", discipline_name)


def push_scholar_knowledge(
    scholar_name: str,
    affiliation: str | None = None,
    works_count: int | None = None,
    cited_by_count: int | None = None,
    *,
    openalex_id: str | None = None,
) -> None:
    client = get_zep_client()
    _ensure_user()

    content = f"Scholar: {scholar_name}."
    if affiliation:
        content += f" Affiliation: {affiliation}."
    if works_count:
        content += f" Published {works_count} works."
    if cited_by_count:
        content += f" Cited by {cited_by_count} works."

    meta = _base_metadata(
        memory_type="insight",
        origin="external",
        confidence="high",
        verification="peer_reviewed",
        evidence_ref=f"openalex_{openalex_id}" if openalex_id else "",
        source_id=f"scholar_{scholar_name}",
    )

    client.graph.add(
        data=content,
        type="text",
        user_id=USER_SYSTEM,
        graph_id=GRAPH_ID,
        metadata=meta,
    )
    logger.info("Pushed scholar knowledge: %s", scholar_name)


def push_debate_summary(
    debate_title: str,
    disciplines: list[str],
    mode: str,
    proposition: str | None,
    consensus: str | None,
    disagreements: str | None,
    open_questions: str | None,
    directions: str | None,
    *,
    debate_id: int | None = None,
    summary_message_id: int | None = None,
) -> None:
    """Push a completed debate's summary into Zep as reusable knowledge."""
    client = get_zep_client()
    _ensure_user()

    disc_str = ", ".join(disciplines)
    parts = [
        f"Academic debate summary — disciplines: {disc_str}.",
        f"Title: {debate_title}. Mode: {mode}.",
    ]
    if proposition:
        parts.append(f"Proposition: {proposition}.")
    if consensus:
        parts.append(f"Consensus reached: {consensus}")
    if disagreements:
        parts.append(f"Key disagreements: {disagreements}")
    if open_questions:
        parts.append(f"Open questions: {open_questions}")
    if directions:
        parts.append(f"Suggested research directions: {directions}")

    content = "\n".join(parts)

    memory_type = "consensus" if consensus else "disagreement"
    meta = _base_metadata(
        memory_type=memory_type,
        origin="generated",
        confidence="medium",
        evidence_ref=f"debate_msg_{summary_message_id}" if summary_message_id
                     else (f"debate_{debate_id}" if debate_id else ""),
        source_id=f"debate_{debate_id}" if debate_id else "",
    )

    try:
        client.graph.add(
            data=content,
            type="text",
            user_id=USER_SYSTEM,
            graph_id=GRAPH_ID,
            metadata=meta,
        )
        logger.info("Pushed debate summary to Zep: %s", debate_title)
    except Exception as e:
        logger.warning("Failed to push debate summary to Zep: %s", e)


def push_hypothesis(
    discipline_names: list[str],
    hypothesis_text: str,
    model_name: str,
) -> None:
    """Push an AI-generated research hypothesis into Zep."""
    client = get_zep_client()
    _ensure_user()

    disc_str = ", ".join(discipline_names)
    content = (
        f"AI-generated research hypothesis for the intersection of: {disc_str}.\n"
        f"Model: {model_name}.\n"
        f"Hypothesis: {hypothesis_text}"
    )

    meta = _base_metadata(
        memory_type="insight",
        origin="generated",
        confidence="low",
        evidence_ref="",
    )

    try:
        client.graph.add(
            data=content,
            type="text",
            user_id=USER_SYSTEM,
            graph_id=GRAPH_ID,
            metadata=meta,
        )
        logger.info("Pushed hypothesis to Zep: %s", disc_str)
    except Exception as e:
        logger.warning("Failed to push hypothesis to Zep: %s", e)


# ---------------------------------------------------------------------------
# Search / Retrieval
# ---------------------------------------------------------------------------

def _build_metadata_filter(
    origin: str | None = None,
    memory_type: str | None = None,
) -> SearchFilters | None:
    """Build Zep SearchFilters from our metadata constraints."""
    filters: list[EpisodeMetadataFilter] = []

    if origin:
        filters.append(EpisodeMetadataFilter(
            property_name="origin",
            comparison_operator="=",
            property_value=origin,
        ))
    if memory_type:
        filters.append(EpisodeMetadataFilter(
            property_name="memory_type",
            comparison_operator="=",
            property_value=memory_type,
        ))

    if not filters:
        return None

    return SearchFilters(
        episode_metadata_filters=MetadataFilterGroup(
            type="and",
            filters=filters,
        )
    )


def _rerank_by_origin(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Re-rank search results: external origin gets boosted, generated gets dampened."""
    for r in results:
        raw_score = r.get("score") or 0.0
        origin = r.get("origin", "generated")
        weight = ORIGIN_WEIGHT.get(origin, 1.0)
        r["weighted_score"] = raw_score * weight
    return sorted(results, key=lambda x: x.get("weighted_score", 0), reverse=True)


def search_knowledge(
    query: str,
    limit: int = 5,
    *,
    user_id: str = USER_SYSTEM,
    origin: str | None = None,
    memory_type: str | None = None,
) -> list[dict[str, Any]]:
    client = get_zep_client()
    search_filters = _build_metadata_filter(origin=origin, memory_type=memory_type)
    try:
        kwargs: dict[str, Any] = {
            "query": query,
            "user_id": user_id,
            "graph_id": GRAPH_ID,
            "limit": limit,
        }
        if search_filters:
            kwargs["search_filters"] = search_filters

        results = client.graph.search(**kwargs)
        edges = results.edges or []
        items = []
        for e in edges:
            fact = e.fact if hasattr(e, "fact") else str(e)
            score = e.score if hasattr(e, "score") else None
            ep_meta = {}
            if hasattr(e, "episodes") and e.episodes:
                ep = e.episodes[0] if isinstance(e.episodes, list) else None
                if ep and hasattr(ep, "metadata") and ep.metadata:
                    ep_meta = ep.metadata
            items.append({
                "fact": fact,
                "score": score,
                "origin": ep_meta.get("origin", "generated"),
                "memory_type": ep_meta.get("memory_type", ""),
                "evidence_ref": ep_meta.get("evidence_ref", ""),
                "confidence": ep_meta.get("confidence", ""),
                "verification": ep_meta.get("verification", ""),
            })
        return _rerank_by_origin(items)
    except Exception as e:
        logger.warning("Zep search failed: %s", e)
        return []


def retrieve_context(
    query: str,
    limit: int = 5,
    *,
    user_id: str = USER_SYSTEM,
    origin: str | None = None,
    memory_type: str | None = None,
) -> str:
    """Search Zep and return a formatted context string ready for LLM injection."""
    results = search_knowledge(
        query, limit=limit,
        user_id=user_id, origin=origin, memory_type=memory_type,
    )
    if not results:
        return ""
    lines = []
    for r in results:
        fact = r.get("fact", "")
        if fact:
            tag = "[external]" if r.get("origin") == "external" else "[generated]"
            lines.append(f"- {tag} {fact}")
    return "\n".join(lines)
