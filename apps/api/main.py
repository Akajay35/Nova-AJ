from __future__ import annotations

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Nova-AJ API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "name": "Nova-AJ",
        "status": "online",
        "service": "api",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "Nova-AJ API",
    }


@app.get("/api/status")
def status() -> dict[str, str]:
    return {
        "name": "Nova-AJ",
        "status": "online",
        "environment": os.getenv("RENDER_SERVICE_NAME", "render"),
    }
