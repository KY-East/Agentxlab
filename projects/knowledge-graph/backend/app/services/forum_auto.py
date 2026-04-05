"""Auto-generate forum posts from completed debates and high-score sparks."""

from __future__ import annotations

import json
import logging

from sqlalchemy.orm import Session

from app.models.debate import Debate
from app.models.forum import ForumPost
from app.models.spark import Spark

logger = logging.getLogger(__name__)

SPARK_HIGHLIGHT_THRESHOLD = 0.8


def auto_create_debate_post(debate: Debate, db: Session) -> ForumPost | None:
    """Create an AI-zone forum post summarising a completed debate."""
    existing = (
        db.query(ForumPost)
        .filter(ForumPost.debate_id == debate.id, ForumPost.post_type == "debate_summary")
        .first()
    )
    if existing:
        return existing

    disc_names = [d.name_en for d in debate.disciplines]
    disc_names_zh = [d.name_zh or d.name_en for d in debate.disciplines]

    sparks = (
        db.query(Spark)
        .filter(Spark.debate_id == debate.id)
        .order_by(Spark.novelty_score.desc())
        .all()
    )

    spark_section = ""
    if sparks:
        lines = []
        for s in sparks[:10]:
            score_bar = "★" * int(s.novelty_score * 5)
            lines.append(f"- **[{s.novelty_type}]** {s.content} ({score_bar} {s.novelty_score:.2f})")
        spark_section = "\n\n---\n\n### Cross-Domain Sparks\n\n" + "\n".join(lines)

    content_parts = []
    if debate.summary_consensus:
        content_parts.append(f"### Consensus\n\n{debate.summary_consensus}")
    if debate.summary_disagreements:
        content_parts.append(f"### Disagreements\n\n{debate.summary_disagreements}")
    if debate.summary_open_questions:
        content_parts.append(f"### Open Questions\n\n{debate.summary_open_questions}")
    if debate.summary_directions:
        content_parts.append(f"### Research Directions\n\n{debate.summary_directions}")

    content = "\n\n".join(content_parts) + spark_section

    title = f"[AI] {debate.title}"

    post = ForumPost(
        user_id=None,
        title=title,
        content=content,
        zone="ai_generated",
        post_type="debate_summary",
        status="theory_ready" if debate.summary_directions else "open",
        debate_id=debate.id,
        discipline_tags=json.dumps(disc_names_zh),
    )
    db.add(post)
    db.flush()

    logger.info("Auto-created debate summary post %d for debate %d", post.id, debate.id)
    return post


def highlight_top_sparks(debate_id: int, db: Session) -> list[ForumPost]:
    """Create pinned spark-highlight posts for sparks above the threshold."""
    sparks = (
        db.query(Spark)
        .filter(
            Spark.debate_id == debate_id,
            Spark.novelty_score >= SPARK_HIGHLIGHT_THRESHOLD,
        )
        .order_by(Spark.novelty_score.desc())
        .all()
    )

    posts = []
    for spark in sparks:
        existing = (
            db.query(ForumPost)
            .filter(ForumPost.spark_id == spark.id, ForumPost.post_type == "spark_highlight")
            .first()
        )
        if existing:
            continue

        title = f"[Spark] {spark.content[:80]}{'…' if len(spark.content) > 80 else ''}"
        content = (
            f"**Type:** {spark.novelty_type}\n"
            f"**Score:** {spark.novelty_score:.2f}\n\n"
            f"{spark.content}\n\n"
        )
        if spark.reasoning:
            content += f"**Reasoning:** {spark.reasoning}\n"

        post = ForumPost(
            user_id=None,
            title=title,
            content=content,
            zone="ai_generated",
            post_type="spark_highlight",
            status="open",
            debate_id=debate_id,
            spark_id=spark.id,
            is_pinned=True,
        )
        db.add(post)
        posts.append(post)

    if posts:
        db.flush()
        logger.info("Created %d spark highlight posts for debate %d", len(posts), debate_id)

    return posts
