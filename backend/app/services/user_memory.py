"""User Memory Engine — builds a preference profile from history + saved outfits."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class UserProfile:
    """Lightweight summary of a user's style preferences derived from data."""

    frequent_colors: list[str] = field(default_factory=list)   # top-N palette colors
    frequent_vibes: list[str] = field(default_factory=list)    # top-N style tags
    frequent_occasions: list[str] = field(default_factory=list)
    liked_outfit_ids: set[str] = field(default_factory=set)    # saved / hearted
    past_outfit_ids: set[str] = field(default_factory=set)     # previously recommended
    total_interactions: int = 0

    @property
    def has_history(self) -> bool:
        return self.total_interactions > 0

    def summary_text(self) -> str:
        """One-paragraph summary suitable for injecting into an LLM prompt."""
        parts: list[str] = []
        if self.frequent_vibes:
            parts.append(f"Preferred vibes: {', '.join(self.frequent_vibes[:5])}")
        if self.frequent_colors:
            parts.append(f"Favorite colors: {', '.join(self.frequent_colors[:5])}")
        if self.frequent_occasions:
            parts.append(f"Common occasions: {', '.join(self.frequent_occasions[:4])}")
        if self.liked_outfit_ids:
            parts.append(f"Has {len(self.liked_outfit_ids)} saved/liked outfits")
        if not parts:
            return "New user with no style history yet."
        return ". ".join(parts) + "."


class UserMemoryEngine:
    """Builds a *UserProfile* from raw history + saved-outfit payloads."""

    def build_profile(
        self,
        history_payloads: list[dict[str, Any]],
        saved_payloads: list[dict[str, Any]],
        top_n: int = 5,
    ) -> UserProfile:
        color_counter: Counter[str] = Counter()
        vibe_counter: Counter[str] = Counter()
        occasion_counter: Counter[str] = Counter()
        liked_ids: set[str] = set()
        past_ids: set[str] = set()

        # --- Saved / liked outfits (stronger signal, weight ×2) ---
        for p in saved_payloads:
            oid = _safe_str(p.get("outfit_id") or p.get("id"))
            if oid:
                liked_ids.add(oid)
            for c in _extract_colors(p):
                color_counter[c] += 2
            for t in _extract_tags(p):
                vibe_counter[t] += 2

        # --- Past recommendations (normal weight) ---
        for p in history_payloads:
            oid = _safe_str(p.get("outfit_id"))
            if oid:
                past_ids.add(oid)
            for c in _extract_colors(p):
                color_counter[c] += 1
            for t in _extract_tags(p):
                vibe_counter[t] += 1
            ctx = p.get("context")
            if isinstance(ctx, dict):
                occ = _safe_str(ctx.get("occasion"))
                if occ:
                    occasion_counter[occ] += 1

        return UserProfile(
            frequent_colors=[c for c, _ in color_counter.most_common(top_n)],
            frequent_vibes=[v for v, _ in vibe_counter.most_common(top_n)],
            frequent_occasions=[o for o, _ in occasion_counter.most_common(top_n)],
            liked_outfit_ids=liked_ids,
            past_outfit_ids=past_ids,
            total_interactions=len(history_payloads) + len(saved_payloads),
        )


# ── helpers ──────────────────────────────────────────────────────────────

def _safe_str(val: Any) -> str:
    if isinstance(val, str) and val.strip():
        return val.strip()
    return ""


def _extract_colors(payload: dict[str, Any]) -> list[str]:
    """Pull palette colors from an outfit payload."""
    colors: list[str] = []
    for c in payload.get("palette", []) or []:
        if isinstance(c, str) and c.strip():
            colors.append(c.strip().lower())
    for item in payload.get("items", []) or []:
        if isinstance(item, dict):
            for c in item.get("colors", []) or []:
                if isinstance(c, str) and c.strip():
                    colors.append(c.strip().lower())
    return colors


def _extract_tags(payload: dict[str, Any]) -> list[str]:
    """Pull style tags from an outfit payload."""
    tags: list[str] = []
    for t in payload.get("tags", []) or []:
        if isinstance(t, str) and t.strip():
            tags.append(t.strip().lower())
    for item in payload.get("items", []) or []:
        if isinstance(item, dict):
            for t in item.get("tags", []) or []:
                if isinstance(t, str) and t.strip():
                    tags.append(t.strip().lower())
    return tags
