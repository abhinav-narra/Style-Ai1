from __future__ import annotations

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ....core.config import Settings
from ...deps import settings_dep


router = APIRouter()

FASHION_SYSTEM_PROMPT = """You are DRIP AI — a trendy, knowledgeable, and friendly AI fashion stylist.

Your expertise covers:
- Fashion styles, trends, and history
- Color theory and palette advice for different skin tones
- Fabric types, care instructions, and seasonal dressing
- Body type styling, proportions, and silhouettes
- Wardrobe building, capsule wardrobes, and budgeting
- Brand recommendations across all price ranges
- Accessories, grooming, and overall styling
- Cultural and occasion-appropriate dressing

Personality:
- Warm, supportive, and encouraging
- Use emojis sparingly but naturally (1-2 per response)
- Give concrete, actionable advice
- Keep responses concise (2-4 short paragraphs max)
- Use bullet points for lists
- Reference current trends when relevant

If someone asks something completely unrelated to fashion/style/beauty, politely redirect:
"That's outside my fashion expertise! But I'd love to help you with styling, outfits, colors, or trends. What can I style for you? 💫"
"""


class ChatRequest(BaseModel):
    message: str
    history: list[dict[str, str]] = Field(default_factory=list)


class ChatResponse(BaseModel):
    reply: str


@router.post("/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    settings: Settings = Depends(settings_dep),
):
    api_key = settings.groq_api_key
    if not api_key:
        raise HTTPException(status_code=503, detail="GROQ_API_KEY not configured")

    model = settings.groq_model

    # Build messages list with system prompt + conversation history + new message
    messages = [{"role": "system", "content": FASHION_SYSTEM_PROMPT}]

    # Add conversation history (last 10 messages for context window management)
    for msg in payload.history[-10:]:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": payload.message})

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1024,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            reply = data["choices"][0]["message"]["content"]
            return ChatResponse(reply=reply)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"Groq API error: {e.response.status_code}") from e
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Chat service unavailable: {str(e)}") from e
