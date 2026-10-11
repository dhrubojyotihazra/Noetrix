import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import health, parse, score, rank, improver, export

app = FastAPI(
    title="Noetrix ATS Engine API",
    description="Deterministic 6-metric hybrid ATS resume scoring, tailoring, and ranking engine.",
    version="1.0.0"
)

# CORS middleware: read allowed origins from ALLOWED_ORIGINS env var (default localhost:3000 only, no "*")
raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
allowed_origins = [o.strip() for o in raw_origins.split(",") if o.strip()]
if not allowed_origins:
    allowed_origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
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
