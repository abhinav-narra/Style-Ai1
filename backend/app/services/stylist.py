from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from ..core.config import Settings
from ..models.schemas import AnalyzeResponse, RecommendRequest, RecommendResponse, ScoredOutfit
from ..repositories.history import HistoryRepository
from ..repositories.saved_outfits import SavedOutfitRepository
from ..utils.images import decode_base64_image_to_bgr, decode_image_bytes_to_bgr, extract_color_palette_labels
from .diversity import DiversityEngine
from .face_detection import FaceDetector
from .image_search import ImageSearchService
from .llm import LlmContext, LlmRecommender
from .outfit_scoring import OutfitCatalog, OutfitScoringEngine, ScoringContext
from .skin_tone import SkinToneDetector
from .user_memory import UserMemoryEngine, UserProfile


@dataclass(frozen=True)
class AnalyzeArtifacts:
    analyze: AnalyzeResponse
    raw: dict[str, Any]


class StylistService:
    def __init__(self, settings: Settings, history_repo: HistoryRepository, saved_repo: SavedOutfitRepository | None = None):
        self._settings = settings
        self._history = history_repo
        self._saved = saved_repo
        self._faces = FaceDetector()
        self._skin = SkinToneDetector()
        self._catalog = OutfitCatalog()
        self._scorer = OutfitScoringEngine()
        self._diversity = DiversityEngine()
        self._llm = LlmRecommender()
        self._memory = UserMemoryEngine()
        self._image_search = ImageSearchService(settings)

    async def analyze_image_bytes(self, image_bytes: bytes) -> AnalyzeArtifacts:
        bgr = decode_image_bytes_to_bgr(image_bytes)
        det = self._faces.detect(bgr)
        dominant = None
        if det.faces:
            dominant = self._skin.detect(bgr, det.faces[0]).skin_tone
        analyze = AnalyzeResponse(faces=det.faces, dominant_skin_tone=dominant)
        raw = analyze.model_dump()
        # Attach coarse color palette labels for downstream outfit ranking.
        try:
            raw["color_palette"] = extract_color_palette_labels(bgr)
        except DependencyMissingError:
            raw["color_palette"] = []
        return AnalyzeArtifacts(analyze=analyze, raw=raw)

    async def analyze_image_base64(self, image_base64: str) -> AnalyzeArtifacts:
        bgr = decode_base64_image_to_bgr(image_base64)
        det = self._faces.detect(bgr)
        dominant = None
        if det.faces:
            dominant = self._skin.detect(bgr, det.faces[0]).skin_tone
        analyze = AnalyzeResponse(faces=det.faces, dominant_skin_tone=dominant)
        raw = analyze.model_dump()
        try:
            raw["color_palette"] = extract_color_palette_labels(bgr)
        except DependencyMissingError:
            raw["color_palette"] = []
        return AnalyzeArtifacts(analyze=analyze, raw=raw)

    async def recommend(self, req: RecommendRequest, image_bytes: bytes | None = None) -> RecommendResponse:
        analyze_artifacts: AnalyzeArtifacts | None = None
        if image_bytes:
            analyze_artifacts = await self.analyze_image_bytes(image_bytes)
        elif req.image_base64:
            analyze_artifacts = await self.analyze_image_base64(req.image_base64)

        skin = analyze_artifacts.analyze.dominant_skin_tone if analyze_artifacts else None

        # Palette can be supplied by caller OR derived from skin tone / image analysis.
        palette_from_req: list[str] = []
        maybe_palette = (req.extra_context or {}).get("color_palette")
        if isinstance(maybe_palette, list):
            palette_from_req = [str(x).strip().lower() for x in maybe_palette if str(x).strip()]

        # If no explicit palette, generate one from skin tone (primary) or image analysis (fallback)
        if not palette_from_req and skin:
            palette_from_req = _generate_skin_palette(skin.tone, getattr(skin, 'undertone', 'neutral'))
        elif not palette_from_req and analyze_artifacts:
            maybe_analyze_palette = analyze_artifacts.raw.get("color_palette") or []
            if isinstance(maybe_analyze_palette, list):
                palette_from_req = [
                    str(x).strip().lower() for x in maybe_analyze_palette if str(x).strip()
                ]

        palette_temperature = _palette_temperature(palette_from_req)
        vibe = _extract_vibe(req.style_preferences)

        # ── Build user memory profile ──────────────────────────────────
        history_rows = await self._history.list_recent(req.user_id, limit=50)
        history_payloads = [r.payload for r in history_rows]

        saved_payloads: list[dict[str, Any]] = []
        if self._saved:
            saved_rows = await self._saved.list_for_user(req.user_id, limit=100)
            saved_payloads = [r.payload for r in saved_rows]

        user_profile = self._memory.build_profile(history_payloads, saved_payloads)

        ctx = ScoringContext(
            occasion=req.occasion,
            style_preferences=req.style_preferences,
            budget=req.budget,
            skin_tone=skin,
            color_palette=palette_from_req,
            vibe=vibe,
            palette_temperature=palette_temperature,
            culture=req.culture,
            gender=req.gender,
            user_profile=user_profile,
        )

        candidates = self._catalog.list_candidates()
        scored = self._scorer.score(candidates, ctx)

        # Diversity via user history
        diversified = self._diversity.apply(scored, history_payloads)

        # Ensure top 4 are visually distinct (unique images + not overly similar palettes/tags)
        diversified = _select_visually_diverse(diversified, top_k=5, ensure_unique_top=4)

        # ── Ensure at least 4 results (1 top + 3 alternatives) ────────
        top: list[ScoredOutfit] = diversified[:5]
        while len(top) < 4 and len(scored) > len(top):
            # Pad with lower-ranked outfits not already in top
            top_ids = {o.outfit.outfit_id for o in top}
            for s in scored:
                if s.outfit.outfit_id not in top_ids:
                    top.append(s)
                    top_ids.add(s.outfit.outfit_id)
                    if len(top) >= 4:
                        break

        # ── Compute confidence + explanation per outfit ────────────────
        top = _enrich_with_confidence(top, user_profile)

        llm_ctx = LlmContext(
            user_id=req.user_id,
            occasion=req.occasion,
            style_preferences=req.style_preferences,
            budget=req.budget,
            skin_tone=skin.model_dump() if skin else None,
            top_outfits=[s.model_dump() for s in top],
            gender=req.gender,
            user_profile_summary=user_profile.summary_text() if user_profile.has_history else None,
        )
        text = await self._llm.generate(llm_ctx, self._settings)

        # Enhance top outfits with dynamic images from Unsplash/Pexels before returning
        for scored in top:
            # Build strict query string: "{gender} {vibe} {occasion} {culture} outfit {color}"
            q_parts = []
            g = req.gender.lower() if req.gender else ""
            if g == "male":
                q_parts.append("male menswear")
            elif g == "female":
                q_parts.append("female womenswear")
            elif g in ["non-binary", "unisex", "prefer-not", "prefer not to say"]:
                q_parts.append("unisex androgynous fashion")
            elif g:
                q_parts.append(g)

            if vibe:
                q_parts.append(vibe)
            if req.occasion:
                q_parts.append(req.occasion)
            if req.culture:
                q_parts.append(req.culture)
            
            q_parts.append("outfit")
            
            # Incorporate top palette color if available
            if scored.outfit.palette:
                q_parts.append(scored.outfit.palette[0])
            
            query = " ".join(q_parts)
            
            img_result = await self._image_search.search_outfit_images(query)
            if img_result:
                scored.outfit.image = img_result.url
                if not scored.outfit.vibe_images:
                    scored.outfit.vibe_images = []
                # Ensure the main image is also the first vibe image
                if scored.outfit.vibe_images:
                    scored.outfit.vibe_images[0] = img_result.url
                else:
                    scored.outfit.vibe_images.append(img_result.url)

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


def _enrich_with_confidence(outfits: list[ScoredOutfit], profile: UserProfile) -> list[ScoredOutfit]:
    """Compute confidence score and explanation for each outfit."""
    enriched: list[ScoredOutfit] = []
    for s in outfits:
        # Confidence = weighted blend of match score, history affinity, trend
        match_norm = min(1.0, max(0.0, s.score / 100.0))
        trend = float(s.outfit.trend_score or 0.5)

        # History affinity (inline quick calc)
        if profile.has_history:
            outfit_tags = {t.lower() for t in s.outfit.tags}
            outfit_colors = {c.lower() for c in s.outfit.palette}
            fav_colors = set(profile.frequent_colors)
            fav_vibes = set(profile.frequent_vibes)
            color_ov = len(outfit_colors & fav_colors) / max(1, len(fav_colors)) if fav_colors else 0.0
            vibe_ov = len(outfit_tags & fav_vibes) / max(1, len(fav_vibes)) if fav_vibes else 0.0
            hist_aff = 0.5 * color_ov + 0.5 * vibe_ov
        else:
            hist_aff = 0.5

        confidence = round(100.0 * (0.50 * match_norm + 0.30 * hist_aff + 0.20 * trend), 1)

        # Build explanation
        parts: list[str] = []
        if s.reasons:
            parts.append(s.reasons[0])  # lead with top reason
        if profile.has_history:
            matching_vibes = set(profile.frequent_vibes) & {t.lower() for t in s.outfit.tags}
            if matching_vibes:
                parts.append(f"Matches your love for {', '.join(list(matching_vibes)[:2])}")
            matching_colors = set(profile.frequent_colors) & {c.lower() for c in s.outfit.palette}
            if matching_colors:
                parts.append(f"Uses your favorite tones: {', '.join(list(matching_colors)[:2])}")
        if trend >= 0.7:
            parts.append("Currently trending")
        explanation = ". ".join(parts) + "." if parts else "Great match for your request."

        enriched.append(ScoredOutfit(
            outfit=s.outfit,
            score=s.score,
            reasons=s.reasons,
            diversity_penalty=s.diversity_penalty,
            confidence=confidence,
            explanation=explanation,
        ))
    return enriched


def _generate_skin_palette(tone: str, undertone: str = "neutral") -> list[str]:
    """
    Generate a dynamic color palette from skin tone depth × undertone.

    Matrix:
      - warm undertone  → earth tones, beige, olive, brown, cream
      - cool undertone  → blue, grey, white, black, navy
      - neutral         → universal mix of both
      - deep skin       → bold, high-contrast colors
      - fair skin       → soft pastels
    """
    # ── Base palette by undertone ──
    warm_base = ["beige", "olive", "brown", "tan", "deep-green", "stone"]
    cool_base = ["navy", "charcoal", "white", "grey", "pastel-blue", "light-blue"]
    neutral_base = ["white", "charcoal", "beige", "navy", "olive", "grey"]

    if undertone == "warm":
        base = warm_base
    elif undertone == "cool":
        base = cool_base
    else:
        base = neutral_base

    # ── Modify by skin depth ──
    if tone == "deep":
        # Bold, high-contrast colors that pop against deep skin
        boldify = {"beige": "white", "stone": "gold", "grey": "cobalt", "pastel-blue": "crimson"}
        palette = [boldify.get(c, c) for c in base]
        # Ensure at least 2 bold accents
        bold_extras = ["gold", "cobalt", "crimson", "white"]
        for extra in bold_extras:
            if extra not in palette:
                palette.append(extra)
                if len(palette) >= 7:
                    break
    elif tone == "tan":
        # Warm earthy + bold accents
        boldify = {"grey": "navy", "pastel-blue": "deep-green"}
        palette = [boldify.get(c, c) for c in base]
        palette = list(dict.fromkeys(palette + ["white", "brown"]))
    elif tone == "medium":
        # Balanced: earth tones for warm, jewel tones for cool
        if undertone == "warm":
            palette = ["olive", "brown", "deep-green", "tan", "charcoal", "beige"]
        elif undertone == "cool":
            palette = ["navy", "charcoal", "deep-green", "grey", "white", "burgundy"]
        else:
            palette = base
    elif tone == "light":
        # Jewel tones and rich colors
        palette = base.copy()
        jewel_adds = {"beige": "burgundy", "olive": "emerald", "brown": "navy"}
        palette = [jewel_adds.get(c, c) for c in palette]
    elif tone == "very_light":
        # Soft pastels
        pastel_map = {
            "beige": "blush", "olive": "sage", "brown": "lavender",
            "tan": "powder-blue", "deep-green": "mint", "stone": "peach",
            "navy": "lavender", "charcoal": "sage", "white": "blush",
            "grey": "powder-blue", "pastel-blue": "mint", "light-blue": "peach",
        }
        palette = [pastel_map.get(c, c) for c in base]
    else:
        palette = base

    # Remove duplicates while preserving order
    seen: set[str] = set()
    unique: list[str] = []
    for c in palette:
        if c not in seen:
            seen.add(c)
            unique.append(c)
    return unique[:7]


def _extract_vibe(style_preferences: list[str]) -> str | None:
    prefs = [p.strip().lower() for p in (style_preferences or []) if isinstance(p, str) and p.strip()]
    vibe_tokens = {
        "streetwear", "street", "minimal", "minimalist", "classic", "preppy",
        "y2k", "grunge", "coquette", "cottagecore", "dark-academia",
        "coastal", "athleisure", "gym", "sporty",
    }
    for p in prefs:
        if p in vibe_tokens:
            return p
    return None


def _palette_temperature(palette: list[str]) -> str | None:
    warm = {"beige", "tan", "brown", "olive", "deep-green", "dark-brown", "stone"}
    cool = {"white", "grey", "charcoal", "navy", "pastel-blue", "light-blue"}
    p = {c.lower() for c in (palette or [])}
    w = len(p & warm)
    c = len(p & cool)
    if w == 0 and c == 0:
        return None
    return "warm" if w >= c else "cool"


def _features_for_visual(o: ScoredOutfit) -> set[str]:
    feats: set[str] = set()
    if o.outfit.image:
        feats.add(f"img:{o.outfit.image}")
    for t in o.outfit.tags:
        feats.add(f"tag:{t.lower()}")
    for c in o.outfit.palette:
        feats.add(f"color:{c.lower()}")
    return feats


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b) or 1
    return inter / union


def _select_visually_diverse(scored: list[ScoredOutfit], top_k: int, ensure_unique_top: int) -> list[ScoredOutfit]:
    picked: list[ScoredOutfit] = []
    used_images: set[str] = set()
    used_ids: set[str] = set()

    for s in scored:
        if len(picked) >= top_k:
            break
        if s.outfit.outfit_id in used_ids:
            continue
        img = s.outfit.image or ""

        # Hard constraints for the first N results
        if len(picked) < ensure_unique_top:
            if img and img in used_images:
                continue
            too_similar = False
            s_feats = _features_for_visual(s)
            for p in picked:
                if _jaccard(s_feats, _features_for_visual(p)) > 0.75:
                    too_similar = True
                    break
            if too_similar:
                continue

        picked.append(s)
        used_ids.add(s.outfit.outfit_id)
        if img:
            used_images.add(img)

    # If we couldn't fill enough, fall back to remaining while still avoiding duplicates
    if len(picked) < min(top_k, len(scored)):
        for s in scored:
            if len(picked) >= top_k:
                break
            if s.outfit.outfit_id in used_ids:
                continue
            img = s.outfit.image or ""
            if img and img in used_images and len(picked) < ensure_unique_top:
                continue
            picked.append(s)
            used_ids.add(s.outfit.outfit_id)
            if img:
                used_images.add(img)

    return picked

