from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from ..core.errors import DependencyMissingError, InvalidInputError
from ..models.schemas import FaceBox, SkinTone


SkinToneLabel = Literal["very_light", "light", "medium", "tan", "deep"]


@dataclass(frozen=True)
class SkinToneResult:
    skin_tone: SkinTone


class SkinToneDetector:
    """
    Simple skin tone detector based on average color inside a face box.
    This is a baseline heuristic intended for hackathon use; replace with a calibrated model for production.
    """

    def detect(self, bgr_image, face: FaceBox) -> SkinToneResult:
        np = _require_numpy()

        h, w = int(bgr_image.shape[0]), int(bgr_image.shape[1])
        x1 = max(0, min(w - 1, face.x))
        y1 = max(0, min(h - 1, face.y))
        x2 = max(0, min(w, face.x + face.w))
        y2 = max(0, min(h, face.y + face.h))
        if x2 <= x1 or y2 <= y1:
            raise InvalidInputError("Invalid face box for skin tone detection")

        roi = bgr_image[y1:y2, x1:x2]
        if roi.size == 0:
            raise InvalidInputError("Empty ROI for skin tone detection")

        # Sample the center region to reduce hair/background.
        cy1 = int((y2 - y1) * 0.25)
        cy2 = int((y2 - y1) * 0.85)
        cx1 = int((x2 - x1) * 0.2)
        cx2 = int((x2 - x1) * 0.8)
        center = roi[cy1:cy2, cx1:cx2]
        if center.size == 0:
            center = roi

        mean_bgr = center.reshape(-1, 3).mean(axis=0)
        b, g, r = [int(max(0, min(255, v))) for v in mean_bgr.tolist()]
        rgb = (r, g, b)
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        tone = _bucket_by_luma(rgb)
        undertone = _detect_undertone(rgb)
        return SkinToneResult(skin_tone=SkinTone(rgb=rgb, hex=hex_color, tone=tone, undertone=undertone))


def _require_numpy() -> Any:
    try:
        import numpy as np  # type: ignore
    except ModuleNotFoundError as e:
        raise DependencyMissingError("numpy", "Install backend/requirements.txt optional deps") from e
    return np


def _bucket_by_luma(rgb: tuple[int, int, int]) -> SkinToneLabel:
    r, g, b = rgb
    # sRGB relative luminance (rough)
    luma = 0.2126 * r + 0.7152 * g + 0.0722 * b
    if luma >= 200:
        return "very_light"
    if luma >= 170:
        return "light"
    if luma >= 135:
        return "medium"
    if luma >= 105:
        return "tan"
    return "deep"


def _detect_undertone(rgb: tuple[int, int, int]) -> str:
    """Classify undertone as warm/cool/neutral from skin RGB values."""
    r, g, b = rgb
    # Warm undertones have more red/yellow; cool have more blue/pink
    # Use the red-to-blue ratio as primary signal
    if r == 0 and b == 0:
        return "neutral"
    ratio = r / max(b, 1)
    if ratio > 1.3:
        return "warm"
    elif ratio < 0.9:
        return "cool"
    return "neutral"

