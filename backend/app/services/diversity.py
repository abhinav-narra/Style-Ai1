from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from ..models.schemas import ScoredOutfit


@dataclass(frozen=True)
class DiversityConfig:
    max_history: int = 50
    max_penalty: float = 18.0


class DiversityEngine:
    """
    Penalize outfits that are too similar to recent user history.

    Similarity metric:
    - outfit_id exact match => heavy penalty
    - Jaccard similarity over tags + palette => scaled penalty
    """

    def __init__(self, config: DiversityConfig | None = None):
        self._cfg = config or DiversityConfig()

    def apply(self, scored: Iterable[ScoredOutfit], recent_history_payloads: list[dict]) -> list[ScoredOutfit]:
        history = recent_history_payloads[: self._cfg.max_history]
        history_sets = [_features_from_payload(p) for p in history]

        out: list[ScoredOutfit] = []
        for s in scored:
            penalty = 0.0
            for hs in history_sets:
                penalty = max(penalty, _penalty(s, hs, self._cfg.max_penalty))
            out.append(
                ScoredOutfit(
                    outfit=s.outfit,
                    score=round(s.score - penalty, 2),
                    reasons=s.reasons,
                    diversity_penalty=round(penalty, 2),
                )
            )

        out.sort(key=lambda x: x.score, reverse=True)
        return out


def _features_from_payload(payload: dict) -> set[str]:
    feats: set[str] = set()
    oid = payload.get("outfit_id")
    if isinstance(oid, str):
        feats.add(f"oid:{oid}")
    img = payload.get("image")
    if isinstance(img, str) and img:
        feats.add(f"img:{img}")
    for t in payload.get("tags", []) or []:
        if isinstance(t, str):
            feats.add(f"tag:{t.lower()}")
    for c in payload.get("palette", []) or []:
        if isinstance(c, str):
            feats.add(f"color:{c.lower()}")
    for it in payload.get("items", []) or []:
        if isinstance(it, dict):
            name = it.get("name")
            if isinstance(name, str):
                feats.add(f"item:{name.lower()}")
            for t in it.get("tags", []) or []:
                if isinstance(t, str):
                    feats.add(f"tag:{t.lower()}")
    return feats


def _penalty(s: ScoredOutfit, history_feats: set[str], max_penalty: float) -> float:
    current_feats = _features_from_payload(
        {
            "outfit_id": s.outfit.outfit_id,
            "tags": s.outfit.tags,
            "palette": s.outfit.palette,
            "items": [it.model_dump() for it in s.outfit.items],
        }
    )
    if f"oid:{s.outfit.outfit_id}" in history_feats:
        return max_penalty

    inter = len(current_feats & history_feats)
    union = len(current_feats | history_feats) or 1
    jaccard = inter / union
    return min(max_penalty, max_penalty * jaccard * 0.9)

