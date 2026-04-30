"""KPAX service package — bootstraps Agent X Lab import path.

─────────────────────────────────────────────────────────────────────
⚠️ LEGACY INFRASTRUCTURE — EXCEPTION-REGISTERED IN PROJECT.md §5.1
─────────────────────────────────────────────────────────────────────

The sys.path hack below exists ONLY to support the two legacy routers
(`routers/analyze.py`, `routers/report.py`) which still import from
`app.*` (AXL's monorepo). All other KPAX code (services, v1_analyze,
clients, token_ledger) is already clean and does NOT need this hack.

This hack gets deleted together with the legacy routers on KPAX v0
frontend-PRD completion day (see PROJECT.md §5.1 rule #6 exception
block). Do NOT add new `from app.*` imports anywhere in KPAX.
"""

import sys
from pathlib import Path

_AXL_BACKEND = Path(__file__).resolve().parent.parent.parent.parent / "projects" / "knowledge-graph" / "backend"
if str(_AXL_BACKEND) not in sys.path:
    sys.path.insert(0, str(_AXL_BACKEND))
