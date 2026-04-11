from __future__ import annotations

from sqlalchemy import (
    Column, DateTime, ForeignKey, Integer, String, Text, Boolean, UniqueConstraint, func,
)

from app.models.base import Base


class ForumPost(Base):
    __tablename__ = "forum_posts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    title = Column(String(300), nullable=False)
    content = Column(Text, nullable=False, server_default="")

    zone = Column(String(20), nullable=False, server_default="community", index=True)
    post_type = Column(String(30), nullable=False, server_default="discussion", index=True)
    status = Column(String(20), nullable=False, server_default="open", index=True)

    debate_id = Column(Integer, ForeignKey("debates.id"), nullable=True, index=True)
    spark_id = Column(Integer, ForeignKey("sparks.id"), nullable=True)
    parent_post_id = Column(Integer, ForeignKey("forum_posts.id"), nullable=True)

    discipline_tags = Column(Text, nullable=True)

    vote_score = Column(Integer, nullable=False, server_default="0")
    comment_count = Column(Integer, nullable=False, server_default="0")
    is_pinned = Column(Boolean, nullable=False, server_default="0")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ForumComment(Base):
    __tablename__ = "forum_comments"

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("forum_posts.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("forum_comments.id"), nullable=True)
    content = Column(Text, nullable=False)
    vote_score = Column(Integer, nullable=False, server_default="0")
    comment_type = Column(String(20), nullable=False, server_default="normal")

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ForumVote(Base):
    __tablename__ = "forum_votes"
    __table_args__ = (
        UniqueConstraint("user_id", "target_type", "target_id", name="uq_user_vote"),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    target_type = Column(String(10), nullable=False)
    target_id = Column(Integer, nullable=False)
    vote_type = Column(Integer, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TranslationCache(Base):
    __tablename__ = "translation_cache"
    __table_args__ = (
        UniqueConstraint("content_type", "content_id", "field", "target_lang", name="uq_translation"),
    )

    id = Column(Integer, primary_key=True)
    content_type = Column(String(20), nullable=False, index=True)
    content_id = Column(Integer, nullable=False, index=True)
    field = Column(String(20), nullable=False)
    target_lang = Column(String(5), nullable=False)
    translated_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
