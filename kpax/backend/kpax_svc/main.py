"""KPAX — Decision analysis API."""

from __future__ import annotations

import kpax_svc  # noqa: F401 — triggers AXL path setup

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from kpax_svc.routers import analyze, report, v1_analyze

app = FastAPI(
    title="KPAX — Decision Analysis",
    version="0.1.0",
    description="Your life is the sum of your choices.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router)
app.include_router(v1_analyze.router)
app.include_router(report.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "product": "kpax"}
