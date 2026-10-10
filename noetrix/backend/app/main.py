"""Noetrix Backend Application Entry Point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import health, parse, score, rank, improver, export

app = FastAPI(
    title="Noetrix ATS Engine API",
    description="Deterministic 6-metric hybrid ATS resume scoring, tailoring, and ranking engine.",
    version="1.0.0"
)

# CORS middleware allowing frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows Vercel preview URLs, localhost, and custom domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(health.router)
app.include_router(parse.router)
app.include_router(score.router)
app.include_router(rank.router)
app.include_router(improver.router)
app.include_router(export.router)


@app.get("/")
def root():
    return {
        "message": "Welcome to Noetrix ATS Engine API",
        "documentation": "/docs",
        "health": "/api/health"
    }
