"""Context collector: manages analysis session state.

Holds the full lifecycle of a single analysis — question, parsed fields,
user answers, supplements — and compiles everything into a structured
prompt context for the expert debate.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class AnalysisSession:
    session_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    question: str = ""
    question_type: str = "general"
    question_summary: str = ""
    context_fields: list[dict] = field(default_factory=list)
    user_answers: dict[str, Any] = field(default_factory=dict)
    supplements: list[str] = field(default_factory=list)
    expert_lineup: list[dict] = field(default_factory=list)
    disciplines: list[str] = field(default_factory=list)
    debate_id: int | None = None
    report: dict | None = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = "idle"


_sessions: dict[str, AnalysisSession] = {}


def create_session(question: str, parsed: dict) -> AnalysisSession:
    """Create a new analysis session from the parsed question output."""
    session = AnalysisSession(
        question=question,
        question_type=parsed.get("question_type", "general"),
        question_summary=parsed.get("question_summary", question),
        context_fields=parsed.get("context_fields", []),
        status="collecting_context",
    )
    _sessions[session.session_id] = session
    return session


def get_session(session_id: str) -> AnalysisSession | None:
    return _sessions.get(session_id)


def update_answers(session_id: str, answers: dict[str, Any]) -> AnalysisSession | None:
    session = _sessions.get(session_id)
    if not session:
        return None
    session.user_answers.update(answers)
    session.status = "previewing"
    return session


def add_supplement(session_id: str, text: str) -> AnalysisSession | None:
    session = _sessions.get(session_id)
    if not session:
        return None
    session.supplements.append(text)
    return session


def build_prompt_context(session: AnalysisSession) -> str:
    """Compile all collected info into a single prompt block for experts."""
    parts = [f"用户的核心问题：{session.question}"]

    if session.user_answers:
        parts.append("\n用户提供的背景信息：")
        field_map = {f["field_id"]: f for f in session.context_fields}
        for fid, val in session.user_answers.items():
            f = field_map.get(fid)
            label = f["label"] if f else fid
            if isinstance(val, list):
                val = "、".join(str(v) for v in val)
            parts.append(f"- {label}：{val}")

    if session.supplements:
        parts.append("\n用户补充说明：")
        for s in session.supplements:
            parts.append(f"- {s}")

    return "\n".join(parts)


def set_expert_lineup(session_id: str, lineup: list[dict]) -> None:
    session = _sessions.get(session_id)
    if session:
        session.expert_lineup = lineup
        session.status = "previewing"


def set_debate_id(session_id: str, debate_id: int) -> None:
    session = _sessions.get(session_id)
    if session:
        session.debate_id = debate_id
        session.status = "debating"


def set_report(session_id: str, report: dict) -> None:
    session = _sessions.get(session_id)
    if session:
        session.report = report
        session.status = "report_ready"
