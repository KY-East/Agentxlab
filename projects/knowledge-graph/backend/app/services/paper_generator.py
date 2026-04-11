"""Iterative paper generation — outline creation and section-by-section writing."""

from __future__ import annotations

import json
import logging

from sqlalchemy.orm import Session, selectinload

from app.models.debate import Debate
from app.models.paper_draft import PaperDraft, PaperSection
from app.models import Paper, Discipline
from app.services.ai_provider import chat_completion

logger = logging.getLogger(__name__)

OUTLINE_SYSTEM_PROMPTS = {
    "en": """\
You are a senior academic writing advisor at Agent X Lab. Your task is to create
a detailed paper outline based on an interdisciplinary academic debate and a chosen
research direction.

The outline should follow standard academic paper structure and be suitable for
a research paper at the intersection of multiple disciplines.

Respond ONLY with valid JSON (no markdown fences, no extra text) matching this schema:
{
  "title": "<paper title>",
  "sections": [
    {
      "heading": "<section title>",
      "summary": "<2-3 sentence description of what this section will cover>"
    }
  ]
}

Generate 5-8 sections. Always include: Introduction, Literature Review (or Background),
Methodology, Analysis/Results, Discussion, and Conclusion. Add domain-specific sections
as appropriate for the research direction.
All output must be in English.""",
    "zh": """\
你是 Agent X Lab 的高级学术写作顾问。你的任务是根据一场跨学科学术辩论和所选的研究方向，\
创建详细的论文大纲。

大纲应遵循标准学术论文结构，适合跨学科研究论文。

仅以有效的 JSON 格式回复（无 markdown 代码块，无额外文本），格式如下：
{
  "title": "<论文标题>",
  "sections": [
    {
      "heading": "<章节标题>",
      "summary": "<2-3句描述该章节的内容>"
    }
  ]
}

生成 5-8 个章节。必须包含：引言、文献综述（或背景）、方法论、分析/结果、讨论和结论。\
根据研究方向添加领域相关章节。
所有输出必须为中文。""",
}

SECTION_SYSTEM_PROMPTS = {
    "en": """\
You are a senior academic writer at Agent X Lab. You are writing one section of
an interdisciplinary research paper.

Guidelines:
- Write in formal academic prose, suitable for a peer-reviewed journal.
- Integrate knowledge from all relevant disciplines.
- Reference specific theories, scholars, and findings where appropriate.
- When citing papers, use inline references like (Author, Year).
- Maintain coherence with previously written sections.
- Target 800-1500 words for this section.
- Be substantive and detailed, not superficial.
- All output must be in English.""",
    "zh": """\
你是 Agent X Lab 的高级学术作者。你正在撰写一篇跨学科研究论文的一个章节。

撰写指南：
- 使用正式学术文体，适合同行评审期刊。
- 整合所有相关学科的知识。
- 适当引用具体理论、学者和研究成果。
- 引用论文时使用行内引用格式如（作者，年份）。
- 与已撰写的章节保持连贯。
- 本章节目标 800-1500 字。
- 内容要充实详细，不要流于表面。
- 所有输出必须为中文。""",
}


def _get_zep_context(query: str) -> str:
    """Best-effort Zep retrieval."""
    try:
        from app.services.zep_manager import retrieve_context
        return retrieve_context(query, limit=5)
    except Exception:
        return ""


def _get_related_papers(discipline_ids: list[int], db: Session, limit: int = 10) -> str:
    """Fetch top-cited papers linked to intersections that contain the given disciplines."""
    from app.models.intersection import intersection_discipline, intersection_paper

    ix_ids_subq = (
        db.query(intersection_discipline.c.intersection_id)
        .filter(intersection_discipline.c.discipline_id.in_(discipline_ids))
        .subquery()
    )

    papers = (
        db.query(Paper)
        .join(intersection_paper, intersection_paper.c.paper_id == Paper.id)
        .filter(intersection_paper.c.intersection_id.in_(db.query(ix_ids_subq)))
        .filter(Paper.citation_count.isnot(None))
        .order_by(Paper.citation_count.desc())
        .limit(limit)
        .all()
    )

    if not papers:
        return ""

    lines = []
    for p in papers:
        cite = f"{p.title}"
        if p.year:
            cite += f" ({p.year})"
        if p.citation_count:
            cite += f" [cited {p.citation_count}x]"
        if p.abstract:
            cite += f"\n  Abstract: {p.abstract[:200]}..."
        lines.append(f"- {cite}")

    return "Relevant published papers:\n" + "\n".join(lines)


async def generate_outline(debate: Debate, direction: str, db: Session, *, user_id: int | None = None) -> PaperDraft:
    """Generate a paper outline from a completed debate + chosen direction."""
    lang = getattr(debate, "language", "zh") or "zh"
    if lang not in ("zh", "en"):
        lang = "zh"

    disc_names = [d.name_en for d in debate.disciplines]
    disc_ids = [d.id for d in debate.disciplines]
    topic = " x ".join(disc_names)

    zep_ctx = _get_zep_context(f"{topic} {direction}")
    papers_ctx = _get_related_papers(disc_ids, db)

    debate_summary = _format_debate_summary(debate)

    user_prompt = (
        f"## Research Direction\n{direction}\n\n"
        f"## Disciplines Involved\n{topic}\n\n"
        f"## Debate Summary\n{debate_summary}\n\n"
    )
    if zep_ctx:
        user_prompt += f"## Knowledge Base Context\n{zep_ctx}\n\n"
    if papers_ctx:
        user_prompt += f"## Related Published Research\n{papers_ctx}\n\n"
    user_prompt += "Create a detailed paper outline for this research direction."

    outline_prompt = OUTLINE_SYSTEM_PROMPTS.get(lang, OUTLINE_SYSTEM_PROMPTS["en"])
    raw = await chat_completion(
        messages=[
            {"role": "system", "content": outline_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.4,
        max_tokens=3000,
        user_id=user_id,
        db=db,
    )

    parsed = _parse_json_response(raw)

    title = parsed.get("title", f"Research Paper: {direction[:80]}")
    sections_data = parsed.get("sections", [])

    if not sections_data:
        sections_data = [
            {"heading": "Introduction", "summary": "Introduction to the research topic."},
            {"heading": "Literature Review", "summary": "Review of existing research."},
            {"heading": "Methodology", "summary": "Research methodology."},
            {"heading": "Analysis", "summary": "Analysis and results."},
            {"heading": "Discussion", "summary": "Discussion of findings."},
            {"heading": "Conclusion", "summary": "Conclusions and future work."},
        ]

    draft = PaperDraft(
        title=title,
        debate_id=debate.id,
        direction=direction,
        status="outline",
    )
    db.add(draft)
    db.flush()

    for i, sec in enumerate(sections_data):
        section = PaperSection(
            draft_id=draft.id,
            sort_order=i,
            heading=sec.get("heading", f"Section {i + 1}"),
            summary=sec.get("summary", ""),
            status="pending",
        )
        db.add(section)

    db.flush()
    return draft


async def generate_section_content(
    draft: PaperDraft,
    section: PaperSection,
    db: Session,
    *,
    user_id: int | None = None,
) -> PaperSection:
    """Generate content for a single paper section."""
    debate = draft.debate
    disc_names = [d.name_en for d in debate.disciplines]
    disc_ids = [d.id for d in debate.disciplines]
    topic = " x ".join(disc_names)

    zep_ctx = _get_zep_context(f"{topic} {section.heading}")
    papers_ctx = _get_related_papers(disc_ids, db, limit=8)
    debate_summary = _format_debate_summary(debate)

    prior_sections = _format_prior_sections(draft, section.sort_order)

    user_prompt = (
        f"## Paper Title\n{draft.title}\n\n"
        f"## Research Direction\n{draft.direction}\n\n"
        f"## Current Section\n"
        f"Heading: {section.heading}\n"
        f"Description: {section.summary or 'N/A'}\n"
    )
    if section.writing_instruction:
        user_prompt += f"Author's instruction: {section.writing_instruction}\n"
    user_prompt += "\n"

    if prior_sections:
        user_prompt += f"## Previously Written Sections\n{prior_sections}\n\n"

    user_prompt += f"## Debate Summary (source material)\n{debate_summary}\n\n"

    if zep_ctx:
        user_prompt += f"## Knowledge Base Context\n{zep_ctx}\n\n"
    if papers_ctx:
        user_prompt += f"## Citable Papers\n{papers_ctx}\n\n"

    user_prompt += (
        f"Write the full content for the section \"{section.heading}\". "
        f"Be detailed and substantive."
    )

    section.status = "generating"
    if draft.status == "outline":
        draft.status = "writing"
    db.flush()

    lang = getattr(debate, "language", "zh") or "zh"
    if lang not in ("zh", "en"):
        lang = "zh"
    section_prompt = SECTION_SYSTEM_PROMPTS.get(lang, SECTION_SYSTEM_PROMPTS["en"])

    content = await chat_completion(
        messages=[
            {"role": "system", "content": section_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.6,
        max_tokens=4000,
        user_id=user_id,
        db=db,
    )

    is_regeneration = section.content is not None
    section.content = content
    section.status = "completed"
    if is_regeneration:
        section.version += 1
    db.flush()

    all_done = all(s.status == "completed" for s in draft.sections)
    if all_done:
        draft.status = "completed"
        db.flush()

    return section


def _format_debate_summary(debate: Debate) -> str:
    parts = []
    if debate.summary_consensus:
        parts.append(f"Consensus: {debate.summary_consensus}")
    if debate.summary_disagreements:
        parts.append(f"Disagreements: {debate.summary_disagreements}")
    if debate.summary_open_questions:
        parts.append(f"Open Questions: {debate.summary_open_questions}")
    if debate.summary_directions:
        parts.append(f"Suggested Directions: {debate.summary_directions}")
    if debate.proposition:
        parts.append(f"Debate Proposition: {debate.proposition}")
    return "\n\n".join(parts) if parts else "No summary available."


def _format_prior_sections(draft: PaperDraft, current_sort_order: int) -> str:
    """Format already-completed sections for context continuity."""
    parts = []
    for s in draft.sections:
        if s.sort_order < current_sort_order and s.content:
            text = s.content[:1500]
            if len(s.content) > 1500:
                text += "\n[... truncated for context ...]"
            parts.append(f"### {s.heading}\n{text}")
    return "\n\n".join(parts)


def export_markdown(draft: PaperDraft) -> str:
    """Export the entire draft as a Markdown document."""
    lines = [f"# {draft.title}\n"]

    if draft.direction:
        lines.append(f"*Research Direction: {draft.direction}*\n")

    lines.append("---\n")

    for section in draft.sections:
        lines.append(f"## {section.heading}\n")
        if section.content:
            lines.append(section.content)
        else:
            lines.append(f"*[Pending — {section.summary or 'No description'}]*")
        lines.append("")

    return "\n".join(lines)


def _parse_json_response(raw: str) -> dict:
    text = raw.strip()
    if text.startswith("```"):
        first_newline = text.index("\n")
        last_fence = text.rfind("```")
        text = text[first_newline + 1:last_fence].strip()
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError) as exc:
        logger.error("Failed to parse LLM outline response: %s", exc)
        return {}


def _parse_json_array(raw: str) -> list:
    text = raw.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        return []
    try:
        parsed = json.loads(text[start : end + 1])
        return parsed if isinstance(parsed, list) else []
    except json.JSONDecodeError:
        return []


SUGGEST_PROMPTS = {
    "en": """\
You are a senior academic advisor at Agent X Lab. Based on a completed \
interdisciplinary debate, suggest 2-3 compelling research directions that could \
become full papers.

For each direction, provide:
- "title": a concise paper title
- "description": 1-2 sentence explanation of the angle
- "estimated_sections": number between 5 and 8

Respond ONLY with a JSON array. All output in English.""",
    "zh": """\
你是 Agent X Lab 的高级学术顾问。根据一场已完成的跨学科辩论，\
建议 2-3 个有吸引力的研究方向，可以发展成完整论文。

对于每个方向，提供：
- "title": 简洁的论文标题
- "description": 1-2 句解释该角度
- "estimated_sections": 5 到 8 之间的数字

仅以 JSON 数组格式回复。所有输出使用中文。""",
}

CHAT_REFINE_PROMPTS = {
    "en": """\
You are an academic writing advisor. The user is refining a paper outline through \
conversation. Given the current outline and the user's request, produce the updated \
outline.

Respond ONLY with valid JSON matching this schema:
{
  "title": "<updated title>",
  "sections": [{"heading": "<title>", "summary": "<description>"}],
  "reply": "<brief natural-language reply to the user>"
}
All output in English.""",
    "zh": """\
你是学术写作顾问。用户正在通过对话完善论文大纲。\
根据当前大纲和用户的请求，生成更新后的大纲。

仅以有效的 JSON 格式回复：
{
  "title": "<更新后的标题>",
  "sections": [{"heading": "<章节标题>", "summary": "<章节描述>"}],
  "reply": "<对用户的简短自然语言回复>"
}
所有输出使用中文。""",
}


async def suggest_directions(debate: Debate, db: Session, *, user_id: int | None = None) -> list[dict]:
    """Suggest 2-3 research directions from a completed debate."""
    lang = getattr(debate, "language", "zh") or "zh"
    if lang not in ("zh", "en"):
        lang = "zh"

    disc_names = [d.name_en for d in debate.disciplines]
    topic = " x ".join(disc_names)
    debate_summary = _format_debate_summary(debate)

    user_prompt = (
        f"## Disciplines\n{topic}\n\n"
        f"## Debate Summary\n{debate_summary}\n\n"
        "Suggest 2-3 research directions."
    )

    prompt = SUGGEST_PROMPTS.get(lang, SUGGEST_PROMPTS["en"])
    raw = await chat_completion(
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.5,
        max_tokens=1500,
        user_id=user_id,
        db=db,
    )

    parsed = _parse_json_array(raw)
    results = []
    for item in parsed[:3]:
        results.append({
            "title": item.get("title", "Untitled"),
            "description": item.get("description", ""),
            "estimated_sections": max(5, min(8, int(item.get("estimated_sections", 6)))),
        })

    if not results:
        fallback_title = topic if lang == "en" else topic
        results = [
            {"title": f"Research Paper: {fallback_title}", "description": debate_summary[:100], "estimated_sections": 6},
        ]

    return results


async def refine_outline_via_chat(
    debate: Debate,
    current_title: str,
    current_sections: list[dict],
    user_message: str,
    db: Session,
    *,
    user_id: int | None = None,
) -> dict:
    """Refine an outline based on user's natural language instruction."""
    lang = getattr(debate, "language", "zh") or "zh"
    if lang not in ("zh", "en"):
        lang = "zh"

    outline_json = json.dumps(
        {"title": current_title, "sections": current_sections},
        ensure_ascii=False,
    )

    user_prompt = (
        f"## Current Outline\n```json\n{outline_json}\n```\n\n"
        f"## User Request\n{user_message}"
    )

    prompt = CHAT_REFINE_PROMPTS.get(lang, CHAT_REFINE_PROMPTS["en"])
    raw = await chat_completion(
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.4,
        max_tokens=3000,
        user_id=user_id,
        db=db,
    )

    parsed = _parse_json_response(raw)
    return {
        "title": parsed.get("title", current_title),
        "sections": parsed.get("sections", current_sections),
        "reply": parsed.get("reply", ""),
    }


async def generate_all_sections(draft: PaperDraft, db: Session, *, user_id: int | None = None):
    """Async generator: generate all pending sections one by one.

    Yields dict events for SSE streaming:
      {"event": "section_start", "section_id": ..., "heading": ...}
      {"event": "section_done",  "section_id": ..., "heading": ...}
      {"event": "all_done"}
    """
    debate = (
        db.query(Debate)
        .options(selectinload(Debate.disciplines))
        .get(draft.debate_id)
    )
    if not debate:
        yield {"event": "error", "message": "Debate not found"}
        return

    draft.debate = debate
    pending = [s for s in sorted(draft.sections, key=lambda s: s.sort_order) if s.status != "completed"]

    for section in pending:
        yield {"event": "section_start", "section_id": section.id, "heading": section.heading}
        try:
            await generate_section_content(draft, section, db, user_id=user_id)
            db.commit()
            yield {"event": "section_done", "section_id": section.id, "heading": section.heading}
        except Exception as exc:
            logger.error("Failed to generate section %d: %s", section.id, exc)
            yield {"event": "section_error", "section_id": section.id, "heading": section.heading, "error": str(exc)}

    yield {"event": "all_done"}
