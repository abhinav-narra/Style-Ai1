from __future__ import annotations

import logging
import os

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter()

SYSTEM_PROMPT = "You are an elite AI fashion stylist. You recommend outfits, accessories, colors, and trends based on user mood, culture, weather, and occasion. Never give generic answers."

class ChatRequest(BaseModel):
    message: str
    history: list[dict[str, str]] = Field(default_factory=list)

class ChatResponse(BaseModel):
    reply: str

async def generate_chat_response(user_message: str, history: list[dict[str, str]]) -> str:
    # Read API key securely from environment
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        logger.error("GROQ_API_KEY not found in environment variables")
        return "Stylist is thinking... try again"

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Add conversation history
    for msg in history[-10:]:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": user_message})

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {groq_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": messages,
                    "temperature": 0.7,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Groq API error: {e}")
        return "Stylist is thinking... try again"


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    """Chat endpoint strictly connecting to Groq via backend."""
    reply = await generate_chat_response(payload.message, payload.history)
    return ChatResponse(reply=reply)
