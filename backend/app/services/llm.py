from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from ..core.config import Settings
from ..utils.json_safe import safe_json_loads


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LlmContext:
    user_id: str
    occasion: str | None
    style_preferences: list[str]
    budget: str | None
    skin_tone: dict[str, Any] | None
    top_outfits: list[dict[str, Any]]
    gender: str | None = None
    user_profile_summary: str | None = None


class LlmRecommender:
    async def generate(self, ctx: LlmContext, settings: Settings) -> str:
        if settings.openai_api_key:
            try:
                return await _openai_chat(ctx, settings)
            except Exception:
                logger.exception("LLM call failed; falling back to template")
        return _template(ctx)


def _template(ctx: LlmContext) -> str:
    prefs = ", ".join(ctx.style_preferences) if ctx.style_preferences else "your vibe"
    occ = ctx.occasion or "your occasion"
    lines = [f"For {occ}, here are options aligned with {prefs}:"]
    if ctx.user_profile_summary:
        lines.append(f"Based on your style history: {ctx.user_profile_summary}")
    for i, o in enumerate(ctx.top_outfits[:3], start=1):
        outfit = o.get("outfit", {})
        items = outfit.get("items", [])
        item_names = [it.get("name") for it in items if isinstance(it, dict) and it.get("name")]
        conf = o.get("confidence", 0)
        reason = o.get("explanation", "")
        line = f"{i}) " + "; ".join(item_names[:4])
        if conf:
            line += f" (confidence: {conf:.0f}%)"
        if reason:
            line += f" — {reason}"
        lines.append(line)
    return "\n".join(lines)


async def _openai_chat(ctx: LlmContext, settings: Settings) -> str:
    try:
        import httpx  # type: ignore
    except ModuleNotFoundError as e:
        raise RuntimeError("httpx is required for OpenAI calls") from e

    system = (
        "You are an expert fashion stylist. "
        "Return a short recommendation text (max 120 words) that explains why the top outfits work "
        "for this user. Reference their style preferences and explicitly consider their gender when appropriate."
    )
    if ctx.user_profile_summary:
        system += f" User style profile: {ctx.user_profile_summary}"
    user = {
        "user_id": ctx.user_id,
        "gender": ctx.gender,
        "occasion": ctx.occasion,
        "style_preferences": ctx.style_preferences,
        "budget": ctx.budget,
        "skin_tone": ctx.skin_tone,
        "top_outfits": ctx.top_outfits,
        "output_format": {"recommendation_text": "string"},
    }

    payload = {
        "model": settings.openai_model,
        "messages": [
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": (
                    "Given the input JSON, respond ONLY as JSON with key 'recommendation_text'. "
                    f"Input: {user}"
                ),
            },
        ],
        "temperature": 0.7,
    }

    headers = {"Authorization": f"Bearer {settings.openai_api_key}", "Content-Type": "application/json"}
    url = settings.openai_base_url.rstrip("/") + "/chat/completions"

    timeout = httpx.Timeout(20.0, connect=10.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()

    content = (
        data.get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
    )
    parsed = safe_json_loads(content)
    if parsed.ok and isinstance(parsed.value, dict) and isinstance(parsed.value.get("recommendation_text"), str):
        return parsed.value["recommendation_text"].strip()

    # If model returned plain text, accept it.
    if isinstance(content, str) and content.strip():
        return content.strip()

    return _template(ctx)

