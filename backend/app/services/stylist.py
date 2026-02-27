from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from ..core.config import Settings
from ..models.schemas import AnalyzeResponse, RecommendRequest, RecommendResponse, ScoredOutfit
from ..repositories.history import HistoryRepository
from ..utils.images import decode_base64_image_to_bgr, decode_image_bytes_to_bgr
from .diversity import DiversityEngine
from .face_detection import FaceDetector
from .llm import LlmContext, LlmRecommender
from .outfit_scoring import OutfitCatalog, OutfitScoringEngine, ScoringContext
from .skin_tone import SkinToneDetector


@dataclass(frozen=True)
class AnalyzeArtifacts:
    analyze: AnalyzeResponse
    raw: dict[str, Any]


class StylistService:
    def __init__(self, settings: Settings, history_repo: HistoryRepository):
        self._settings = settings
        self._history = history_repo
        self._faces = FaceDetector()
        self._skin = SkinToneDetector()
        self._catalog = OutfitCatalog()
        self._scorer = OutfitScoringEngine()
        self._diversity = DiversityEngine()
        self._llm = LlmRecommender()

    async def analyze_image_bytes(self, image_bytes: bytes) -> AnalyzeArtifacts:
        bgr = decode_image_bytes_to_bgr(image_bytes)
        det = self._faces.detect(bgr)
        dominant = None
        if det.faces:
            dominant = self._skin.detect(bgr, det.faces[0]).skin_tone
        analyze = AnalyzeResponse(faces=det.faces, dominant_skin_tone=dominant)
        raw = analyze.model_dump()
        return AnalyzeArtifacts(analyze=analyze, raw=raw)

    async def analyze_image_base64(self, image_base64: str) -> AnalyzeArtifacts:
        bgr = decode_base64_image_to_bgr(image_base64)
        det = self._faces.detect(bgr)
        dominant = None
        if det.faces:
            dominant = self._skin.detect(bgr, det.faces[0]).skin_tone
        analyze = AnalyzeResponse(faces=det.faces, dominant_skin_tone=dominant)
        raw = analyze.model_dump()
        return AnalyzeArtifacts(analyze=analyze, raw=raw)

    async def recommend(self, req: RecommendRequest, image_bytes: bytes | None = None) -> RecommendResponse:
        analyze_artifacts: AnalyzeArtifacts | None = None
        if image_bytes:
            analyze_artifacts = await self.analyze_image_bytes(image_bytes)
        elif req.image_base64:
            analyze_artifacts = await self.analyze_image_base64(req.image_base64)

        skin = analyze_artifacts.analyze.dominant_skin_tone if analyze_artifacts else None
        ctx = ScoringContext(
            occasion=req.occasion,
            style_preferences=req.style_preferences,
            budget=req.budget,
            skin_tone=skin,
        )

        candidates = self._catalog.list_candidates()
        scored = self._scorer.score(candidates, ctx)

        # Diversity via user history
        history_rows = await self._history.list_recent(req.user_id, limit=50)
        history_payloads = [r.payload for r in history_rows]
        diversified = self._diversity.apply(scored, history_payloads)

        top: list[ScoredOutfit] = diversified[:5]
        llm_ctx = LlmContext(
            user_id=req.user_id,
            occasion=req.occasion,
            style_preferences=req.style_preferences,
            budget=req.budget,
            skin_tone=skin.model_dump() if skin else None,
            top_outfits=[s.model_dump() for s in top],
        )
        text = await self._llm.generate(llm_ctx, self._settings)

        # Persist top outfit to history (memory)
        if top:
            chosen = top[0].outfit
            payload = chosen.model_dump()
            payload["score"] = top[0].score
            payload["diversity_penalty"] = top[0].diversity_penalty
            payload["context"] = {
                "occasion": req.occasion,
                "style_preferences": req.style_preferences,
                "budget": req.budget,
            }
            await self._history.add_entry(req.user_id, chosen.outfit_id, payload)

        return RecommendResponse(
            user_id=req.user_id,
            created_at=datetime.now(timezone.utc),
            recommendation_text=text,
            outfits=top,
        )

