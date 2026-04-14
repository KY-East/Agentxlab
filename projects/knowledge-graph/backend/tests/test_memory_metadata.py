"""Acceptance tests for Memory System Phase 1: metadata schema + retrieval.

Tests verify:
1. All writers produce correct metadata (origin, evidence_ref, memory_type, etc.)
2. _base_metadata helper produces valid structure
3. origin-based re-ranking works (external > generated)
4. _build_metadata_filter constructs correct Zep SearchFilters
5. evidence_ref is non-empty for non-user-profile writes

These are unit tests that mock the Zep client — no real API calls.
"""

from __future__ import annotations

import sys
import os
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ── _base_metadata ──────────────────────────────────────────────

class TestBaseMetadata:
    def test_all_required_keys_present(self):
        from app.services.zep_manager import _base_metadata
        meta = _base_metadata(
            memory_type="consensus",
            origin="external",
            confidence="high",
            verification="peer_reviewed",
            evidence_ref="paper_openalex_W123",
            source_id="debate_42",
        )
        required = {"memory_type", "origin", "source", "source_id",
                     "confidence", "verification", "evidence_ref", "created_at"}
        assert required.issubset(meta.keys())

    def test_origin_must_be_valid(self):
        from app.services.zep_manager import _base_metadata
        meta = _base_metadata(memory_type="insight", origin="external")
        assert meta["origin"] in ("external", "generated")

    def test_max_10_keys(self):
        """Zep metadata limit: max 10 keys."""
        from app.services.zep_manager import _base_metadata
        meta = _base_metadata(memory_type="insight", origin="generated")
        assert len(meta) <= 10

    def test_evidence_ref_defaults_to_empty(self):
        from app.services.zep_manager import _base_metadata
        meta = _base_metadata(memory_type="insight", origin="generated")
        assert meta["evidence_ref"] == ""


# ── Origin-based re-ranking ─────────────────────────────────────

class TestOriginReranking:
    def test_external_ranks_above_generated_same_score(self):
        from app.services.zep_manager import _rerank_by_origin
        items = [
            {"fact": "AI said something", "score": 0.8, "origin": "generated"},
            {"fact": "Paper says X", "score": 0.8, "origin": "external"},
        ]
        ranked = _rerank_by_origin(items)
        assert ranked[0]["origin"] == "external"
        assert ranked[1]["origin"] == "generated"

    def test_high_score_generated_can_beat_low_score_external(self):
        from app.services.zep_manager import _rerank_by_origin
        items = [
            {"fact": "Strong AI insight", "score": 0.95, "origin": "generated"},
            {"fact": "Weak paper ref", "score": 0.5, "origin": "external"},
        ]
        ranked = _rerank_by_origin(items)
        assert ranked[0]["score"] == 0.95

    def test_weighted_scores_calculated(self):
        from app.services.zep_manager import _rerank_by_origin, ORIGIN_WEIGHT
        items = [{"fact": "test", "score": 1.0, "origin": "external"}]
        ranked = _rerank_by_origin(items)
        assert ranked[0]["weighted_score"] == pytest.approx(ORIGIN_WEIGHT["external"])


# ── Metadata filter builder ─────────────────────────────────────

class TestMetadataFilter:
    def test_returns_none_when_no_filters(self):
        from app.services.zep_manager import _build_metadata_filter
        assert _build_metadata_filter() is None

    def test_origin_filter(self):
        from app.services.zep_manager import _build_metadata_filter
        sf = _build_metadata_filter(origin="external")
        assert sf is not None
        group = sf.episode_metadata_filters
        assert group.type == "and"
        assert len(group.filters) == 1
        assert group.filters[0].property_name == "origin"
        assert group.filters[0].property_value == "external"

    def test_combined_filters(self):
        from app.services.zep_manager import _build_metadata_filter
        sf = _build_metadata_filter(origin="generated", memory_type="consensus")
        group = sf.episode_metadata_filters
        assert len(group.filters) == 2
        names = {f.property_name for f in group.filters}
        assert names == {"origin", "memory_type"}


# ── Writer metadata verification ────────────────────────────────

class TestWriterMetadata:
    """Verify each writer passes correct metadata to graph.add."""

    @patch("app.services.zep_manager.get_zep_client")
    def test_push_discipline_has_external_origin(self, mock_client_fn):
        mock_client = MagicMock()
        mock_client_fn.return_value = mock_client

        from app.services.zep_manager import push_discipline_knowledge
        push_discipline_knowledge(
            "Physics", "Study of matter", ["Quantum Mechanics"],
            openalex_id="C12345",
        )

        call_kwargs = mock_client.graph.add.call_args
        meta = call_kwargs.kwargs.get("metadata") or call_kwargs[1].get("metadata")
        assert meta["origin"] == "external"
        assert meta["verification"] == "peer_reviewed"
        assert "openalex_C12345" in meta["evidence_ref"]

    @patch("app.services.zep_manager.get_zep_client")
    def test_push_debate_summary_has_generated_origin(self, mock_client_fn):
        mock_client = MagicMock()
        mock_client_fn.return_value = mock_client

        from app.services.zep_manager import push_debate_summary
        push_debate_summary(
            "Test Debate", ["Physics", "Math"], "structured",
            "Should we?", "Yes", "Some disagree", "What about X?", "Try Y",
            debate_id=42,
        )

        call_kwargs = mock_client.graph.add.call_args
        meta = call_kwargs.kwargs.get("metadata") or call_kwargs[1].get("metadata")
        assert meta["origin"] == "generated"
        assert meta["source_id"] == "debate_42"

    @patch("app.services.zep_manager.get_zep_client")
    def test_push_hypothesis_has_generated_origin(self, mock_client_fn):
        mock_client = MagicMock()
        mock_client_fn.return_value = mock_client

        from app.services.zep_manager import push_hypothesis
        push_hypothesis(["Physics", "Biology"], "Maybe X causes Y", "gpt-5.4")

        call_kwargs = mock_client.graph.add.call_args
        meta = call_kwargs.kwargs.get("metadata") or call_kwargs[1].get("metadata")
        assert meta["origin"] == "generated"
        assert meta["confidence"] == "low"


class TestAgentMemoryMetadata:
    """Verify agent_memory passes metadata through to Zep."""

    @patch("app.services.zep_manager.get_zep_client")
    def test_push_agent_cognition_has_debate_evidence_ref(self, mock_client_fn):
        mock_client = MagicMock()
        mock_client_fn.return_value = mock_client

        from app.services.agent_memory import push_agent_cognition
        push_agent_cognition(1, "professor", "facts", "Gravity is real", debate_id=99)

        call_kwargs = mock_client.graph.add.call_args
        meta = call_kwargs.kwargs.get("metadata") or call_kwargs[1].get("metadata")
        assert meta["origin"] == "generated"
        assert meta["evidence_ref"] == "debate_99"

    @patch("app.services.zep_manager.get_zep_client")
    def test_push_agent_cognition_without_debate_id(self, mock_client_fn):
        mock_client = MagicMock()
        mock_client_fn.return_value = mock_client

        from app.services.agent_memory import push_agent_cognition
        push_agent_cognition(1, "professor", "sparks", "Cross-domain insight")

        call_kwargs = mock_client.graph.add.call_args
        meta = call_kwargs.kwargs.get("metadata") or call_kwargs[1].get("metadata")
        assert meta["evidence_ref"] == ""


# ── Evidence anchor assertion ───────────────────────────────────

class TestEvidenceAnchor:
    """Non-user-profile writes should have non-empty evidence_ref when source is known."""

    @patch("app.services.zep_manager.get_zep_client")
    def test_discipline_with_openalex_has_evidence(self, mock_client_fn):
        mock_client = MagicMock()
        mock_client_fn.return_value = mock_client

        from app.services.zep_manager import push_discipline_knowledge
        push_discipline_knowledge("Physics", "desc", openalex_id="C999")

        meta = mock_client.graph.add.call_args.kwargs.get("metadata") \
               or mock_client.graph.add.call_args[1].get("metadata")
        assert meta["evidence_ref"] != ""

    @patch("app.services.zep_manager.get_zep_client")
    def test_debate_summary_with_id_has_evidence(self, mock_client_fn):
        mock_client = MagicMock()
        mock_client_fn.return_value = mock_client

        from app.services.zep_manager import push_debate_summary
        push_debate_summary(
            "Test", ["A"], "structured", None, "consensus", None, None, None,
            debate_id=7,
        )

        meta = mock_client.graph.add.call_args.kwargs.get("metadata") \
               or mock_client.graph.add.call_args[1].get("metadata")
        assert meta["evidence_ref"] != ""
