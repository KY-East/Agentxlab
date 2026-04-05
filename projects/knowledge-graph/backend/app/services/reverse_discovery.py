"""Reverse Discovery Engine — from research question to discipline recommendations."""

from __future__ import annotations

import json
import logging
from itertools import combinations

from sqlalchemy.orm import Session

from app.models import Discipline, Intersection, intersection_discipline
from app.services.ai_provider import chat_completion

logger = logging.getLogger(__name__)

DISCOVERY_SYSTEM_PROMPT = """You are a research advisor at Agent X Lab, specializing in
identifying interdisciplinary connections. You help researchers find which academic
disciplines are relevant to their research question.

You will be given:
1. A research question in any language
2. A list of available academic disciplines (each with id, English name, Chinese name)

Your task:
1. Analyze the research question and identify which disciplines are most relevant.
2. Select 3-8 disciplines from the provided list.
3. For each selected discipline, explain why it is relevant (one sentence).
4. Recommend 1-3 discipline combinations (each 2-4 disciplines) that form the most
   promising interdisciplinary research angles.
5. For each combination, provide a suggested research direction.

IMPORTANT: Only select disciplines from the provided list. Use their exact IDs.

Respond ONLY with valid JSON matching this schema (no markdown, no extra text):
{
  "matched_disciplines": [
    {
      "discipline_id": <int>,
      "relevance": <float 0-1>,
      "reason_en": "<string>",
      "reason_zh": "<string>"
    }
  ],
  "recommended_combos": [
    {
      "discipline_ids": [<int>, ...],
      "explanation_en": "<string>",
      "explanation_zh": "<string>",
      "direction_en": "<string>",
      "direction_zh": "<string>"
    }
  ]
}"""


def _build_discipline_catalogue(db: Session) -> tuple[str, dict[int, Discipline]]:
    """Fetch all leaf disciplines and format them for the LLM prompt."""
    from sqlalchemy.orm import selectinload

    leaves = (
        db.query(Discipline)
        .options(selectinload(Discipline.children))
        .filter(~Discipline.children.any())
        .all()
    )
    by_id = {d.id: d for d in leaves}

    lines = []
    for d in leaves:
        name_part = d.name_en
        if d.name_zh:
            name_part += f" ({d.name_zh})"
        lines.append(f"  id={d.id}  {name_part}")

    catalogue = "Available disciplines:\n" + "\n".join(lines)
    return catalogue, by_id


def _parse_llm_response(raw: str) -> dict:
    """Extract JSON from LLM response, tolerating markdown fences."""
    text = raw.strip()
    if text.startswith("```"):
        first_newline = text.index("\n")
        last_fence = text.rfind("```")
        text = text[first_newline + 1 : last_fence].strip()
    return json.loads(text)


async def discover(question: str, db: Session) -> dict:
    """Main discovery pipeline: question → LLM → matched disciplines + combos."""
    catalogue, disc_by_id = _build_discipline_catalogue(db)

    user_prompt = (
        f"Research question: {question}\n\n"
        f"{catalogue}\n\n"
        f"Analyze this question and recommend relevant disciplines and combinations."
    )

    raw = await chat_completion(
        messages=[
            {"role": "system", "content": DISCOVERY_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.4,
        max_tokens=3000,
    )

    try:
        parsed = _parse_llm_response(raw)
    except (json.JSONDecodeError, ValueError) as exc:
        logger.error("Failed to parse LLM discovery response: %s", exc)
        raise ValueError("AI 返回格式异常，请重试") from exc

    validated = _validate_and_filter(parsed, disc_by_id)
    enriched = _enrich_results(validated, db)
    return enriched


def _validate_and_filter(parsed: dict, disc_by_id: dict[int, Discipline]) -> dict:
    """Remove any discipline IDs that don't exist in our DB."""
    valid_matches = []
    for m in parsed.get("matched_disciplines", []):
        did = m.get("discipline_id")
        if did in disc_by_id:
            valid_matches.append(m)

    valid_combos = []
    for combo in parsed.get("recommended_combos", []):
        raw_ids = combo.get("discipline_ids", [])
        ids = list(dict.fromkeys(raw_ids))
        if all(did in disc_by_id for did in ids) and len(ids) >= 2:
            combo["discipline_ids"] = ids
            valid_combos.append(combo)

    return {
        "matched_disciplines": valid_matches,
        "recommended_combos": valid_combos,
    }


def _enrich_results(validated: dict, db: Session) -> dict:
    """Add DB information: discipline details, existing intersections, gap status."""
    from sqlalchemy import func

    all_disc_ids = set()
    for m in validated["matched_disciplines"]:
        all_disc_ids.add(m["discipline_id"])
    for c in validated["recommended_combos"]:
        all_disc_ids.update(c["discipline_ids"])

    discs = {
        d.id: d
        for d in db.query(Discipline).filter(Discipline.id.in_(all_disc_ids)).all()
    }

    for m in validated["matched_disciplines"]:
        d = discs.get(m["discipline_id"])
        if d:
            m["name_en"] = d.name_en
            m["name_zh"] = d.name_zh
            m["works_count"] = d.works_count

    for combo in validated["recommended_combos"]:
        ids = sorted(combo["discipline_ids"])
        combo["disciplines"] = [
            {"id": did, "name_en": discs[did].name_en, "name_zh": discs[did].name_zh}
            for did in ids
            if did in discs
        ]

        intersection = _find_exact_intersection(ids, db)
        if intersection:
            combo["existing_intersection_id"] = intersection.id
            combo["intersection_title"] = intersection.title
            combo["is_gap"] = intersection.status == "gap"
        else:
            combo["existing_intersection_id"] = None
            combo["intersection_title"] = None
            combo["is_gap"] = True

    return validated


def _find_exact_intersection(discipline_ids: list[int], db: Session) -> Intersection | None:
    """Find an intersection that contains exactly the given discipline set."""
    from sqlalchemy import func

    n = len(discipline_ids)

    match_subq = (
        db.query(intersection_discipline.c.intersection_id)
        .filter(intersection_discipline.c.discipline_id.in_(discipline_ids))
        .group_by(intersection_discipline.c.intersection_id)
        .having(func.count() == n)
        .subquery()
    )

    total_subq = (
        db.query(
            intersection_discipline.c.intersection_id,
            func.count().label("total"),
        )
        .group_by(intersection_discipline.c.intersection_id)
        .subquery()
    )

    return (
        db.query(Intersection)
        .join(match_subq, Intersection.id == match_subq.c.intersection_id)
        .join(total_subq, Intersection.id == total_subq.c.intersection_id)
        .filter(total_subq.c.total == n)
        .first()
    )
