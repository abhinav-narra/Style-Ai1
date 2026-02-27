from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class FaceBox(BaseModel):
    x: int
    y: int
    w: int
    h: int
    confidence: float = Field(ge=0.0, le=1.0)


class SkinTone(BaseModel):
    rgb: tuple[int, int, int]
    hex: str
    tone: Literal["very_light", "light", "medium", "tan", "deep"]


class AnalyzeResponse(BaseModel):
    faces: list[FaceBox]
    dominant_skin_tone: SkinTone | None = None


class RecommendRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=128)
    occasion: str | None = None
    style_preferences: list[str] = Field(default_factory=list)
    budget: str | None = None
    image_base64: str | None = None
    extra_context: dict[str, Any] = Field(default_factory=dict)


class OutfitItem(BaseModel):
    category: str
    name: str
    colors: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class Outfit(BaseModel):
    outfit_id: str
    items: list[OutfitItem]
    palette: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class ScoredOutfit(BaseModel):
    outfit: Outfit
    score: float
    reasons: list[str] = Field(default_factory=list)
    diversity_penalty: float = 0.0


class RecommendResponse(BaseModel):
    user_id: str
    created_at: datetime
    recommendation_text: str
    outfits: list[ScoredOutfit]


class HistoryEntry(BaseModel):
    user_id: str
    outfit_id: str
    created_at: datetime
    payload: dict[str, Any] = Field(default_factory=dict)


class HistoryResponse(BaseModel):
    user_id: str
    entries: list[HistoryEntry]

