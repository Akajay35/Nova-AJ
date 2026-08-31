from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="Nova-AJ API", version="1.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=10000)


class ChatResponse(BaseModel):
    reply: str
    model: str


def _safe_openai_error(exc: Exception) -> tuple[int, str]:
    """Convert OpenAI SDK errors into useful, non-secret client messages."""
    name = type(exc).__name__.lower()
    message = str(exc).lower()

    if "authentication" in name or "invalid_api_key" in message or "incorrect api key" in message:
        return 401, "OpenAI API key is invalid or not authorized for this project"
    if "permission" in name or "permission" in message or "forbidden" in message:
        return 403, "OpenAI API key does not have permission to use this resource"
    if "rate" in name or "rate_limit" in message or "rate limit" in message:
        return 429, "OpenAI API rate limit reached; try again later"
    if "quota" in message or "billing" in message or "insufficient_quota" in message:
        return 402, "OpenAI API account has no available API quota or billing is required"
    if "not_found" in name or "model" in message and ("not found" in message or "does not exist" in message):
        return 400, "The configured OpenAI model is unavailable to this API project"
    if "timeout" in name or "timed out" in message:
        return 504, "OpenAI API request timed out"

    return 502, "OpenAI API request failed; check the Render service logs for the request error"


@app.get("/")
def root() -> dict[str, str]:
    return {"name": "Nova-AJ", "status": "online", "service": "api"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy", "service": "Nova-AJ API"}


@app.get("/api/status")
def status() -> dict[str, str]:
    return {
        "name": "Nova-AJ",
        "status": "online",
        "environment": os.getenv("RENDER_SERVICE_NAME", "render"),
        "ai_configured": "true" if os.getenv("OPENAI_API_KEY") else "false",
        "model": os.getenv("OPENAI_MODEL", "gpt-5-mini"),
    }


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY is not configured on the server")

    model = os.getenv("OPENAI_MODEL", "gpt-5-mini")

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        response: Any = client.responses.create(
            model=model,
            instructions=(
                "You are Nova-AJ, a helpful personal AI assistant. "
                "Be concise, friendly, and practical. Do not claim to perform actions you cannot perform."
            ),
            input=request.message,
        )
        reply = getattr(response, "output_text", None)
        if not reply:
            raise RuntimeError("OpenAI returned no text response")
        return ChatResponse(reply=reply, model=model)
    except HTTPException:
        raise
    except Exception as exc:
        # Log only exception type/message; never log the API key.
        print(f"Nova-AJ OpenAI error: {type(exc).__name__}: {exc}")
        status_code, detail = _safe_openai_error(exc)
        raise HTTPException(status_code=status_code, detail=detail) from exc
