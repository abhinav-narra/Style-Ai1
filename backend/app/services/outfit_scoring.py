from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from ..models.schemas import Outfit, OutfitItem, ScoredOutfit, SkinTone
from ..utils.hashing import stable_hash


@dataclass(frozen=True)
class ScoringContext:
    occasion: str | None
    style_preferences: list[str]
    budget: str | None
    skin_tone: SkinTone | None


class OutfitCatalog:
    """
    Minimal in-memory catalog.
    Swap this with a database or vector search over a real product catalog.
    """

    def list_candidates(self) -> list[Outfit]:
        outfits: list[Outfit] = []
        outfits.append(
            _mk_outfit(
                items=[
                    ("top", "White linen shirt", ["white"], ["breathable", "classic"]),
                    ("bottom", "Navy chinos", ["navy"], ["smart-casual"]),
                    ("shoes", "Brown loafers", ["brown"], ["leather"]),
                ],
                tags=["smart-casual", "classic", "minimal"],
            )
        )
        outfits.append(
            _mk_outfit(
                items=[
                    ("top", "Black crew-neck tee", ["black"], ["minimal"]),
                    ("bottom", "Light-wash jeans", ["light-blue"], ["everyday"]),
                    ("shoes", "White sneakers", ["white"], ["clean"]),
                ],
                tags=["casual", "street", "minimal"],
            )
        )
        outfits.append(
            _mk_outfit(
                items=[
                    ("top", "Olive bomber jacket", ["olive"], ["streetwear"]),
                    ("top", "Beige turtleneck", ["beige"], ["warm"]),
                    ("bottom", "Black tapered trousers", ["black"], ["sleek"]),
                    ("shoes", "Black boots", ["black"], ["edgy"]),
                ],
                tags=["street", "layered", "modern"],
            )
        )
        outfits.append(
            _mk_outfit(
                items=[
                    ("top", "Pastel blue oxford", ["pastel-blue"], ["preppy"]),
                    ("bottom", "Stone chinos", ["stone"], ["clean"]),
                    ("shoes", "Tan derby shoes", ["tan"], ["leather"]),
                ],
                tags=["office", "preppy", "clean"],
            )
        )
        outfits.append(
            _mk_outfit(
                items=[
                    ("top", "Deep green knit sweater", ["deep-green"], ["cozy"]),
                    ("bottom", "Charcoal wool trousers", ["charcoal"], ["tailored"]),
                    ("shoes", "Dark brown boots", ["dark-brown"], ["winter"]),
                ],
                tags=["winter", "cozy", "elevated"],
            )
        )
        return outfits


class OutfitScoringEngine:
    def score(self, candidates: Iterable[Outfit], ctx: ScoringContext) -> list[ScoredOutfit]:
        scored: list[ScoredOutfit] = []
        prefs = [p.strip().lower() for p in ctx.style_preferences if p.strip()]
        occasion = (ctx.occasion or "").strip().lower()

        for outfit in candidates:
            score = 50.0
            reasons: list[str] = []

            # Occasion fit
            if occasion:
                if "office" in occasion or "work" in occasion:
                    if "office" in outfit.tags or "smart-casual" in outfit.tags or "clean" in outfit.tags:
                        score += 12
                        reasons.append("Good fit for office/work settings.")
                    else:
                        score -= 8
                if "date" in occasion:
                    if "modern" in outfit.tags or "elevated" in outfit.tags or "classic" in outfit.tags:
                        score += 10
                        reasons.append("Date-ready: polished and intentional.")
                if "party" in occasion:
                    if "modern" in outfit.tags or "street" in outfit.tags:
                        score += 8
                        reasons.append("Has a bolder vibe for social events.")

            # Preference alignment
            for p in prefs:
                if p in ("minimal", "minimalist") and "minimal" in outfit.tags:
                    score += 8
                    reasons.append("Matches your minimalist preference.")
                if p in ("street", "streetwear") and ("street" in outfit.tags or "streetwear" in _all_item_tags(outfit)):
                    score += 8
                    reasons.append("Matches your streetwear preference.")
                if p in ("classic", "timeless") and "classic" in outfit.tags:
                    score += 8
                    reasons.append("Matches your classic preference.")
                if p in ("cozy", "warm") and ("cozy" in outfit.tags or "warm" in _all_item_tags(outfit)):
                    score += 6
                    reasons.append("Optimized for warmth and comfort.")

            # Skin tone harmony (simple heuristic)
            if ctx.skin_tone:
                tone = ctx.skin_tone.tone
                palette = [c.lower() for c in outfit.palette]
                if tone in ("deep", "tan") and any(c in palette for c in ("white", "pastel-blue", "stone", "beige")):
                    score += 6
                    reasons.append("High-contrast palette tends to pop nicely.")
                if tone in ("very_light", "light") and any(c in palette for c in ("navy", "charcoal", "deep-green", "olive")):
                    score += 6
                    reasons.append("Deeper tones add flattering contrast.")

            scored.append(ScoredOutfit(outfit=outfit, score=round(score, 2), reasons=_dedupe(reasons)))

        scored.sort(key=lambda s: s.score, reverse=True)
        return scored


def _mk_outfit(items: list[tuple[str, str, list[str], list[str]]], tags: list[str]) -> Outfit:
    outfit_items = [OutfitItem(category=c, name=n, colors=colors, tags=itags) for c, n, colors, itags in items]
    palette: list[str] = []
    for it in outfit_items:
        for c in it.colors:
            if c not in palette:
                palette.append(c)
    payload = {"items": [it.model_dump() for it in outfit_items], "tags": tags, "palette": palette}
    outfit_id = stable_hash(payload)
    return Outfit(outfit_id=outfit_id, items=outfit_items, palette=palette, tags=tags)


def _dedupe(xs: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for x in xs:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def _all_item_tags(outfit: Outfit) -> set[str]:
    tags: set[str] = set()
    for it in outfit.items:
        tags.update(t.lower() for t in it.tags)
    return tags

