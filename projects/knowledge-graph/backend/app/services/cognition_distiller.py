"""Post-debate cognition distillation for Agent persistent memory.

After a debate concludes, this service:
1. Collects each agent's messages from the debate
2. Retrieves the agent's existing cognition from Zep
3. Uses LLM to distill new cognition by comparing old + new
4. Pushes updated cognition back to Zep (rewrite, not append)

Key design principles:
- The threshold for overwriting existing cognition is HIGHER than for writing new
- Facts layer: overwrite only if new evidence is stronger
- Arguments layer: keep original + counterargument, overwrite only if chain is stronger
- Sparks layer: NEVER delete, only add new or compress wording
"""

from __future__ import annotations

import json
import logging

from sqlalchemy.orm import Session

from app.models.debate import Debate, DebateAgent
from app.services.agent_memory import (
    push_agent_cognition,
    retrieve_agent_cognition,
)
from app.services.ai_provider import chat_completion

logger = logging.getLogger(__name__)

DISTILLATION_PROMPT = """\
You are a cognition distillation engine for an AI research agent. Your task is \
to update the agent's accumulated knowledge based on a new debate.

You will receive:
1. The agent's EXISTING cognition (organized in three layers)
2. The agent's MESSAGES from the latest debate
3. The debate CONTEXT (topic, disciplines, summary)

Your job: produce UPDATED cognition for each layer.

## Rules for each layer:

### Facts & Evidence
- Add new verifiable facts learned from this debate
- If a new fact contradicts an existing one with STRONGER evidence, replace it
- If evidence is ambiguous, keep both with notes
- Max ~30 items; if over, compress oldest entries

### Arguments & Stances
- Add new reasoned positions with their logical chains
- If a new argument directly defeats an existing one (stronger logic + evidence), \
replace but KEEP the old argument noted as "superseded by: ..."
- Minority positions with rigorous logic MUST be preserved (science advances by \
challenging consensus)
- Max ~20 items; if over, compress weakest entries

### Cross-Domain Sparks
- Add any new cross-disciplinary connections discovered
- NEVER delete existing sparks — they may become valuable later
- Only compress wording if needed, never remove the core idea
- Mark newly added sparks as "new from debate [topic]"

Respond ONLY with a JSON object:
{
  "facts": ["fact 1", "fact 2", ...],
  "arguments": ["argument 1", ...],
  "sparks": ["spark 1", ...]
}
"""


async def distill_agent_cognition(
    debate: Debate,
    agent: DebateAgent,
    db: Session,
) -> dict[str, list[str]]:
    """Distill cognition for a single agent after a debate.

    Returns the new cognition dict with keys: facts, arguments, sparks.
    """
    if not agent.discipline_id:
        return {"facts": [], "arguments": [], "sparks": []}

    disc_name = agent.discipline.name_en if agent.discipline else "Unknown"
    debate_topic = debate.title

    existing = retrieve_agent_cognition(
        agent.discipline_id, agent.rank,
        query=debate_topic,
        limit=30,
    )

    existing_by_layer: dict[str, list[str]] = {"facts": [], "arguments": [], "sparks": []}
    for item in existing:
        layer = item.get("layer", "facts")
        if layer in existing_by_layer:
            existing_by_layer[layer].append(item["content"])

    agent_messages = [
        m.content for m in debate.messages
        if m.agent_id == agent.id
    ]
    if not agent_messages:
        return existing_by_layer

    summary_parts = []
    if debate.summary_consensus:
        summary_parts.append(f"Consensus: {debate.summary_consensus}")
    if debate.summary_disagreements:
        summary_parts.append(f"Disagreements: {debate.summary_disagreements}")
    if debate.summary_directions:
        summary_parts.append(f"Directions: {debate.summary_directions}")

    disc_names = [d.name_en for d in debate.disciplines]
    context = (
        f"Debate topic: {debate_topic}\n"
        f"Disciplines: {', '.join(disc_names)}\n"
        f"Agent discipline: {disc_name} ({agent.rank})\n"
    )
    if summary_parts:
        context += "Debate summary:\n" + "\n".join(summary_parts)

    user_content = (
        f"## Context\n{context}\n\n"
        f"## Existing Cognition\n"
        f"Facts: {json.dumps(existing_by_layer['facts'], ensure_ascii=False)}\n"
        f"Arguments: {json.dumps(existing_by_layer['arguments'], ensure_ascii=False)}\n"
        f"Sparks: {json.dumps(existing_by_layer['sparks'], ensure_ascii=False)}\n\n"
        f"## Agent's Messages in This Debate\n"
        + "\n---\n".join(agent_messages[:10])
    )

    try:
        raw = await chat_completion(
            [
                {"role": "system", "content": DISTILLATION_PROMPT},
                {"role": "user", "content": user_content},
            ],
            temperature=0.3,
            max_tokens=2000,
        )

        start = raw.index("{")
        end = raw.rindex("}") + 1
        result = json.loads(raw[start:end])
    except Exception as exc:
        logger.warning(
            "Cognition distillation failed for agent %s (disc=%d, rank=%s): %s",
            agent.agent_name, agent.discipline_id, agent.rank, exc,
        )
        return existing_by_layer

    updated: dict[str, list[str]] = {
        "facts": result.get("facts", existing_by_layer["facts"]),
        "arguments": result.get("arguments", existing_by_layer["arguments"]),
        "sparks": _merge_sparks(
            existing_by_layer["sparks"],
            result.get("sparks", []),
        ),
    }

    for layer, items in updated.items():
        for item in items:
            if item.strip():
                push_agent_cognition(
                    agent.discipline_id, agent.rank, layer, item
                )

    logger.info(
        "Distilled cognition for agent %s: %d facts, %d arguments, %d sparks",
        agent.agent_name,
        len(updated["facts"]),
        len(updated["arguments"]),
        len(updated["sparks"]),
    )
    return updated


def _merge_sparks(existing: list[str], new: list[str]) -> list[str]:
    """Merge spark lists: keep ALL existing, add genuinely new ones."""
    merged = list(existing)
    existing_lower = {s.lower().strip() for s in existing}
    for s in new:
        if s.strip() and s.lower().strip() not in existing_lower:
            merged.append(s)
    return merged


async def distill_all_agents(debate: Debate, db: Session) -> None:
    """Run cognition distillation for all non-moderator agents in a debate."""
    for agent in debate.agents:
        if agent.persona == "moderator":
            continue
        if not agent.discipline_id:
            continue
        try:
            await distill_agent_cognition(debate, agent, db)
        except Exception as exc:
            logger.warning(
                "Cognition distillation failed for %s: %s",
                agent.agent_name, exc,
            )
