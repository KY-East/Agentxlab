"""KPAX HTTP clients to external services.

All cross-service communication lives here. KPAX must never import AXL
Python modules directly — Ken's 2026-04-15 hard rule #6. If you need
AXL capability, go through axl_client.
"""
