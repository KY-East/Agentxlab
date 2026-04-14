"""Acceptance tests for Memory System Phase 2: session memory compression.

Tests verify:
1. Compression threshold respects depth setting
2. Messages are correctly split by round
3. Compressed context has three-layer structure (summary + last round raw)
4. Fallback to full history on compression failure
5. No compression for early rounds
"""

from __future__ import annotations

import sys
import os
from unittest.mock import AsyncMock, MagicMock, patch
from types import SimpleNamespace

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.session_memory import (
    _should_compress,
    _split_messages_by_round,
    _format_messages_for_compression,
    _format_messages_as_history,
    build_compressed_context,
    COMPRESSION_THRESHOLD,
)


def _make_msg(round_number: int, content: str, agent_name: str = "Agent A") -> MagicMock:
    msg = MagicMock()
    msg.round_number = round_number
    msg.content = content
    msg.role = "agent"
    msg.agent = SimpleNamespace(agent_name=agent_name)
    return msg


# ── Compression threshold ───────────────────────────────────────

class TestShouldCompress:
    def test_quick_compresses_at_round_2(self):
        assert _should_compress(2, "quick") is True
        assert _should_compress(1, "quick") is False

    def test_standard_compresses_at_round_3(self):
        assert _should_compress(3, "standard") is True
        assert _should_compress(2, "standard") is False

    def test_max_compresses_at_round_4(self):
        assert _should_compress(4, "max") is True
        assert _should_compress(3, "max") is False

    def test_unknown_depth_defaults_to_3(self):
        assert _should_compress(3, "unknown_depth") is True
        assert _should_compress(2, "unknown_depth") is False


# ── Message splitting ───────────────────────────────────────────

class TestSplitByRound:
    def test_groups_correctly(self):
        msgs = [
            _make_msg(1, "R1 msg1"),
            _make_msg(1, "R1 msg2"),
            _make_msg(2, "R2 msg1"),
            _make_msg(3, "R3 msg1"),
        ]
        by_round = _split_messages_by_round(msgs)
        assert set(by_round.keys()) == {1, 2, 3}
        assert len(by_round[1]) == 2
        assert len(by_round[2]) == 1

    def test_none_round_defaults_to_1(self):
        msg = _make_msg(1, "test")
        msg.round_number = None
        by_round = _split_messages_by_round([msg])
        assert 1 in by_round


# ── Format functions ────────────────────────────────────────────

class TestFormatting:
    def test_format_for_compression(self):
        msgs = [_make_msg(1, "Hello"), _make_msg(1, "World", "Agent B")]
        text = _format_messages_for_compression(msgs)
        assert "[Agent A]: Hello" in text
        assert "[Agent B]: World" in text

    def test_format_as_history(self):
        msgs = [_make_msg(1, "Hello")]
        history = _format_messages_as_history(msgs)
        assert len(history) == 1
        assert history[0]["role"] == "user"
        assert "[Agent A]" in history[0]["content"]


# ── Compressed context building ─────────────────────────────────

class TestBuildCompressedContext:
    @pytest.mark.asyncio
    async def test_no_compression_for_early_rounds(self):
        """Round 1-2 with standard depth should return full history."""
        msgs = [_make_msg(1, "msg1"), _make_msg(1, "msg2")]
        result = await build_compressed_context(msgs, 2, depth="standard")
        assert len(result) == 2
        assert all(r["role"] == "user" for r in result)

    @pytest.mark.asyncio
    @patch("app.services.session_memory.chat_completion", new_callable=AsyncMock)
    async def test_compression_produces_three_layer_context(self, mock_chat):
        """Round 3+ should produce: system intro + compressed summary + last round raw."""
        mock_chat.return_value = "## Consensus\n- Everyone agrees on X\n## Unresolved Challenges\n- None"

        msgs = [
            _make_msg(1, "R1 agent A speaks"),
            _make_msg(1, "R1 agent B speaks", "Agent B"),
            _make_msg(2, "R2 agent A responds"),
            _make_msg(2, "R2 agent B responds", "Agent B"),
        ]

        result = await build_compressed_context(msgs, 3, depth="standard", language="zh")

        assert result[0]["role"] == "system"
        assert "未解决" in result[0]["content"] or "Unresolved" in result[0]["content"]

        assert "Consensus" in result[1]["content"] or "共识" in result[1]["content"]

        raw_msgs = [r for r in result[2:] if "R2" in r.get("content", "")]
        assert len(raw_msgs) == 2

    @pytest.mark.asyncio
    @patch("app.services.session_memory.chat_completion", new_callable=AsyncMock)
    async def test_fallback_on_compression_failure(self, mock_chat):
        """If LLM compression fails, fall back to full history."""
        mock_chat.side_effect = Exception("LLM down")

        msgs = [
            _make_msg(1, "R1 msg"),
            _make_msg(2, "R2 msg"),
        ]

        result = await build_compressed_context(msgs, 3, depth="standard")
        assert len(result) == 2
        assert "[Agent A]" in result[0]["content"]

    @pytest.mark.asyncio
    async def test_quick_depth_compresses_earlier(self):
        """depth=quick should compress at round 2."""
        msgs = [_make_msg(1, "R1 msg")]

        with patch("app.services.session_memory.chat_completion", new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = "## Summary\n- compressed"
            result = await build_compressed_context(msgs, 2, depth="quick", language="en")

        assert result[0]["role"] == "system"

    @pytest.mark.asyncio
    async def test_max_depth_no_compression_at_round_3(self):
        """depth=max should NOT compress at round 3."""
        msgs = [
            _make_msg(1, "R1"), _make_msg(2, "R2"),
        ]
        result = await build_compressed_context(msgs, 3, depth="max")
        assert all(r["role"] != "system" or "压缩" not in r.get("content", "") for r in result)


class TestCompressionEfficiency:
    @pytest.mark.asyncio
    @patch("app.services.session_memory.chat_completion", new_callable=AsyncMock)
    async def test_compressed_output_shorter_than_input(self, mock_chat):
        """The compressed context should be shorter than full history."""
        long_content = "A very long argument about quantum mechanics. " * 50
        mock_chat.return_value = "## Consensus\n- Quantum is important"

        msgs = [
            _make_msg(1, long_content),
            _make_msg(1, long_content, "Agent B"),
            _make_msg(2, "R2 short response"),
        ]

        full_history = _format_messages_as_history(msgs)
        full_len = sum(len(m["content"]) for m in full_history)

        compressed = await build_compressed_context(msgs, 3, depth="standard", language="en")
        compressed_len = sum(len(m["content"]) for m in compressed)

        assert compressed_len < full_len
