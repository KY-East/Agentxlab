"""
Zep Cloud integration (SDK v3) — push knowledge into Zep Graph for RAG.

Zep v3 uses Graph API: graph.add(data, type="text") to ingest,
graph.search(query) to retrieve.
"""

from __future__ import annotations

import logging
from typing import Any

from zep_cloud.client import Zep

from app.config import settings

logger = logging.getLogger(__name__)

_client: Zep | None = None
GRAPH_ID = "agent-x-lab"
USER_ID = "system-knowledge"


def get_zep_client() -> Zep:
    global _client
    if _client is None:
        if not settings.zep_api_key:
            raise RuntimeError("ZEP_API_KEY not configured")
        _client = Zep(api_key=settings.zep_api_key)
    return _client


def _ensure_user() -> None:
    client = get_zep_client()
    try:
        client.user.get(USER_ID)
    except Exception:
        client.user.add(user_id=USER_ID)


def push_discipline_knowledge(
    discipline_name: str,
    description: str,
    related_subfields: list[str] | None = None,
) -> None:
    client = get_zep_client()
    _ensure_user()

    content = f"Academic discipline: {discipline_name}."
    if description:
        content += f" Description: {description}."
    if related_subfields:
        content += f" Related subfields: {', '.join(related_subfields)}."

    client.graph.add(
        data=content,
        type="text",
        user_id=USER_ID,
        graph_id=GRAPH_ID,
    )
    logger.info("Pushed discipline knowledge: %s", discipline_name)


def push_scholar_knowledge(
    scholar_name: str,
    affiliation: str | None = None,
    works_count: int | None = None,
    cited_by_count: int | None = None,
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

    client.graph.add(
        data=content,
        type="text",
        user_id=USER_ID,
        graph_id=GRAPH_ID,
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
    try:
        client.graph.add(
            data=content,
            type="text",
            user_id=USER_ID,
            graph_id=GRAPH_ID,
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
    try:
        client.graph.add(
            data=content,
            type="text",
            user_id=USER_ID,
            graph_id=GRAPH_ID,
        )
        logger.info("Pushed hypothesis to Zep: %s", disc_str)
    except Exception as e:
        logger.warning("Failed to push hypothesis to Zep: %s", e)


def search_knowledge(query: str, limit: int = 5) -> list[dict[str, Any]]:
    client = get_zep_client()
    try:
        results = client.graph.search(
            query=query,
            user_id=USER_ID,
            graph_id=GRAPH_ID,
            limit=limit,
        )
        edges = results.edges or []
        return [
            {
                "fact": e.fact if hasattr(e, "fact") else str(e),
                "score": e.score if hasattr(e, "score") else None,
            }
            for e in edges
        ]
    except Exception as e:
        logger.warning("Zep search failed: %s", e)
        return []


def retrieve_context(query: str, limit: int = 5) -> str:
    """Search Zep and return a formatted context string ready for LLM injection."""
    results = search_knowledge(query, limit=limit)
    if not results:
        return ""
    lines = []
    for r in results:
        fact = r.get("fact", "")
        if fact:
            lines.append(f"- {fact}")
    return "\n".join(lines)
