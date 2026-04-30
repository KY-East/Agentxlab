from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.utils.logging_setup import configure_logging, RequestIdMiddleware
import logging

# Install structured JSON logging + request_id filter before any app code runs.
# See app/utils/logging_setup.py for design notes. Ken 2026-04-16 after Lawrence
# methodology tweet.
configure_logging(level=getattr(settings, "log_level", "INFO"))

from app.routers import disciplines, intersections, scholars, papers, graph, ai, gaps, openalex, debate, discovery, paper_gen, sparks, kpax_router

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Agent X Lab — Knowledge Graph API",
    version="0.1.0",
    description="Interdisciplinary knowledge graph for Agent X Lab",
)

if getattr(settings, "auth_bypass_dev_mode", False):
    logger.warning(
        "=" * 70 + "\n"
        "AUTH_BYPASS_DEV_MODE=True — ALL AUTH + QUOTA CHECKS ARE DISABLED.\n"
        "Every request runs as the lowest-id user (dev account).\n"
        "Token limits and allowed_models are bypassed (any LLM in .env is OK).\n"
        "DO NOT deploy with this flag enabled. Set AUTH_BYPASS_DEV_MODE=false\n"
        "or remove the line from .env to restore authentication.\n"
        + "=" * 70
    )

# Request-scoped trace id. Must be added BEFORE CORS so even preflight requests
# get a request_id logged.
app.add_middleware(RequestIdMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(disciplines.router)
app.include_router(intersections.router)
app.include_router(scholars.router)
app.include_router(papers.router)
app.include_router(graph.router)
app.include_router(ai.router)
app.include_router(gaps.router)
app.include_router(openalex.router)
app.include_router(debate.router)
app.include_router(discovery.router)
app.include_router(paper_gen.router)
app.include_router(sparks.router)
app.include_router(kpax_router.router)
app.include_router(kpax_router.followup_router)

try:
    from app.routers import auth, forum, points, subscription
    app.include_router(auth.router)
    app.include_router(forum.router)
    app.include_router(points.router)
    app.include_router(subscription.router)
except ImportError as _auth_exc:
    logger.warning("Auth/forum dependencies not installed (PyJWT / google-auth) — "
                    "/api/auth, /api/forum, /api/points endpoints disabled: %s", _auth_exc)

try:
    from app.routers import zep
    app.include_router(zep.router)
except ImportError:
    logger.warning("zep_cloud SDK not installed — /api/zep endpoints disabled")


@app.get("/api/health")
def health():
    return {"status": "ok"}
