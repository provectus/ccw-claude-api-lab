"""
FastAPI backend for the Claude API Lab — Commercial Loan Underwriting Agent.
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.deps import get_settings
from app.api.routes import pipeline, uploads, stats, schemas

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ensure required directories exist on startup."""
    for d in [settings.upload_dir, settings.processed_dir, settings.fallback_dir]:
        Path(d).mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title="Claude API Lab — Loan Underwriting API",
    description="Agentic pipeline for commercial loan underwriting: parse, validate, compute ratios, and assess creditworthiness",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(pipeline.router)
app.include_router(uploads.router)
app.include_router(stats.router)
app.include_router(schemas.router)


@app.get("/")
async def root():
    return {
        "name": "Claude API Lab — Loan Underwriting API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/api/docs",
    }


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "anthropic_configured": bool(settings.anthropic_api_key),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
