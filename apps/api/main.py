from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="Nova-AJ API", version="1.1.0")

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
        # Do not expose API keys or internal exception details to clients.
        print(f"Nova-AJ chat error: {type(exc).__name__}: {exc}")
        raise HTTPException(status_code=502, detail="AI provider request failed") from exc
