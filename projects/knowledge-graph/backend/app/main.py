from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
import logging

from app.routers import disciplines, intersections, scholars, papers, graph, ai, gaps, openalex, debate, discovery, paper_gen, sparks

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Agent X Lab — Knowledge Graph API",
    version="0.1.0",
    description="Interdisciplinary knowledge graph for Agent X Lab",
)

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
