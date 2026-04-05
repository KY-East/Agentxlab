"""Agent-level persistent memory with three-layer cognition architecture.

Each Agent is identified by (discipline_id, rank) and accumulates cognition
across debates. Memory is stored in Zep Cloud with per-agent user IDs.

Three layers:
  1. Facts & Evidence — objective, verifiable knowledge
  2. Arguments & Stances — reasoned positions with logical chains
  3. Cross-Domain Sparks — creative connections, never auto-deleted

Each layer is stored as a separate Zep graph entry with a structured prefix
so retrieval and distillation can target specific layers.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)

LAYER_PREFIXES = {
    "facts": "[FACT]",
    "arguments": "[ARGUMENT]",
    "sparks": "[SPARK]",
}

LAYER_CAPACITY = {
    "facts": 30,
    "arguments": 20,
    "sparks": 999,
}


def _agent_user_id(discipline_id: int, rank: str) -> str:
    return f"agent-{discipline_id}-{rank}"


def _get_client():
    """Lazy import + init Zep client."""
    from app.services.zep_manager import get_zep_client
    return get_zep_client()


def _ensure_agent_user(discipline_id: int, rank: str) -> str:
    """Ensure the Zep user for this agent identity exists."""
    uid = _agent_user_id(discipline_id, rank)
    client = _get_client()
    try:
        client.user.get(uid)
    except Exception:
        try:
            client.user.add(user_id=uid)
            logger.info("Created Zep agent user: %s", uid)
        except Exception as exc:
            logger.warning("Failed to create Zep agent user %s: %s", uid, exc)
    return uid


def push_agent_cognition(
    discipline_id: int,
    rank: str,
    layer: str,
    content: str,
    *,
    graph_id: str = "agent-x-lab",
) -> None:
    """Push a single cognition item into the agent's Zep memory.

    Args:
        layer: one of "facts", "arguments", "sparks"
        content: the cognition content to store
    """
    if layer not in LAYER_PREFIXES:
        raise ValueError(f"Unknown layer: {layer}")

    uid = _ensure_agent_user(discipline_id, rank)
    prefix = LAYER_PREFIXES[layer]
    tagged = f"{prefix} {content}"

    try:
        client = _get_client()
        client.graph.add(
            data=tagged,
            type="text",
            user_id=uid,
            graph_id=graph_id,
        )
        logger.info("Pushed %s cognition for agent %s", layer, uid)
    except Exception as exc:
        logger.warning("Failed to push cognition for %s: %s", uid, exc)


def retrieve_agent_cognition(
    discipline_id: int,
    rank: str,
    query: str,
    *,
    layer: str | None = None,
    limit: int = 10,
    graph_id: str = "agent-x-lab",
) -> list[dict[str, Any]]:
    """Retrieve cognition entries for an agent, optionally filtered by layer.

    Returns list of {"layer": str, "content": str, "score": float|None}.
    """
    uid = _agent_user_id(discipline_id, rank)

    search_query = query
    if layer and layer in LAYER_PREFIXES:
        search_query = f"{LAYER_PREFIXES[layer]} {query}"

    try:
        client = _get_client()
        results = client.graph.search(
            query=search_query,
            user_id=uid,
            graph_id=graph_id,
            limit=limit,
        )
        edges = results.edges or []
        items = []
        for e in edges:
            fact = e.fact if hasattr(e, "fact") else str(e)
            score = e.score if hasattr(e, "score") else None
            detected_layer = _detect_layer(fact)
            clean = _strip_prefix(fact)
            if layer and detected_layer != layer:
                continue
            items.append({
                "layer": detected_layer,
                "content": clean,
                "score": score,
            })
        return items
    except Exception as exc:
        logger.warning("Agent cognition retrieval failed for %s: %s", uid, exc)
        return []


def format_agent_cognition_for_prompt(
    discipline_id: int,
    rank: str,
    debate_topic: str,
    discipline_name: str,
) -> str | None:
    """Retrieve and format an agent's accumulated cognition for system prompt injection.

    Returns a formatted string or None if no cognition found.
    """
    items = retrieve_agent_cognition(
        discipline_id, rank,
        query=f"{debate_topic} {discipline_name}",
        limit=15,
    )
    if not items:
        return None

    facts = [i["content"] for i in items if i["layer"] == "facts"]
    arguments = [i["content"] for i in items if i["layer"] == "arguments"]
    sparks = [i["content"] for i in items if i["layer"] == "sparks"]

    parts = []
    if facts:
        parts.append("**Your accumulated knowledge (facts):**")
        for f in facts[:10]:
            parts.append(f"- {f}")

    if arguments:
        parts.append("\n**Your developed positions (arguments):**")
        for a in arguments[:8]:
            parts.append(f"- {a}")

    if sparks:
        parts.append("\n**Your cross-domain inspirations (sparks):**")
        for s in sparks[:5]:
            parts.append(f"- {s}")

    if not parts:
        return None

    return (
        "The following is your accumulated cognition from previous debates. "
        "Use it to enrich your arguments, but also be open to revising positions "
        "if presented with stronger evidence.\n\n" + "\n".join(parts)
    )


def _detect_layer(text: str) -> str:
    for layer, prefix in LAYER_PREFIXES.items():
        if text.startswith(prefix):
            return layer
    return "facts"


def _strip_prefix(text: str) -> str:
    for prefix in LAYER_PREFIXES.values():
        if text.startswith(prefix):
            return text[len(prefix):].strip()
    return text
