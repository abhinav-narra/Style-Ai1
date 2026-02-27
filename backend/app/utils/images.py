from __future__ import annotations

import base64
import io
from typing import Any, List

from ..core.errors import DependencyMissingError, InvalidInputError


def _require_numpy_cv2_pil() -> tuple[Any, Any, Any]:
    try:
        import numpy as np  # type: ignore
    except ModuleNotFoundError as e:
        raise DependencyMissingError("numpy", "Install backend/requirements.txt optional deps") from e
    try:
        import cv2  # type: ignore
    except ModuleNotFoundError as e:
        raise DependencyMissingError("opencv-python", "Install backend/requirements.txt optional deps") from e
    try:
        from PIL import Image  # type: ignore
    except ModuleNotFoundError as e:
        raise DependencyMissingError("pillow", "Install backend/requirements.txt optional deps") from e
    return np, cv2, Image


def decode_image_bytes_to_bgr(image_bytes: bytes):
    """
    Decode common image formats into OpenCV BGR ndarray.
    Lazy-imports numpy/cv2/PIL so server can start without them.
    """
    np, cv2, Image = _require_numpy_cv2_pil()
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as e:
        raise InvalidInputError(f"Could not decode image: {e}") from e
    rgb = np.array(img)
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    return bgr


def decode_base64_image_to_bgr(image_base64: str):
    if "," in image_base64:
        # allow data URLs
        image_base64 = image_base64.split(",", 1)[1]
    try:
        raw = base64.b64decode(image_base64, validate=True)
    except Exception as e:
        raise InvalidInputError(f"Invalid base64 image: {e}") from e
    return decode_image_bytes_to_bgr(raw)


def extract_color_palette_labels(bgr_image, k: int = 4) -> List[str]:
    """
    Extract a small set of dominant color labels from a BGR image.

    This is a lightweight k-means over pixels with coarse bucketing into
    human-friendly names that align with the outfit scoring engine, e.g.
    "black", "beige", "olive", "white", "grey", "navy", "light-blue".
    """
    np, cv2, Image = _require_numpy_cv2_pil()

    if bgr_image is None or getattr(bgr_image, "size", 0) == 0:
        return []

    h, w = int(bgr_image.shape[0]), int(bgr_image.shape[1])
    if h <= 0 or w <= 0:
        return []

    # Downsample for speed
    max_side = 200
    if max(h, w) > max_side:
        scale = max_side / float(max(h, w))
        new_w = max(1, int(w * scale))
        new_h = max(1, int(h * scale))
        bgr_image = cv2.resize(bgr_image, (new_w, new_h))

    data = bgr_image.reshape(-1, 3).astype("float32")
    if data.shape[0] == 0:
        return []

    K = max(2, min(k, data.shape[0]))
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 15, 1.0)
    _ret, labels, centers = cv2.kmeans(
        data, K, None, criteria, 3, cv2.KMEANS_PP_CENTERS
    )

    centers = centers.astype("uint8")
    labels_flat = labels.reshape(-1)
    uniq_labels, counts = np.unique(labels_flat, return_counts=True)
    order = np.argsort(counts)[::-1]  # most frequent first

    hsv_centers = cv2.cvtColor(centers.reshape(-1, 1, 3), cv2.COLOR_BGR2HSV).reshape(
        -1, 3
    )

    names: List[str] = []
    for idx in order:
        bgr = centers[uniq_labels[idx]]
        hsv = hsv_centers[uniq_labels[idx]]
        name = _bucket_color_to_name(bgr=bgr, hsv=hsv)
        if name not in names:
            names.append(name)
    return names


def _bucket_color_to_name(bgr, hsv) -> str:
    """
    Map a BGR/HSV color to a coarse palette name.
    Names are chosen to line up with warm/cool sets used by the scorer.
    """
    import numpy as np  # type: ignore

    b, g, r = [int(x) for x in bgr.tolist()]
    h, s, v = [int(x) for x in hsv.tolist()]  # h:0-179, s:0-255, v:0-255

    # Very dark / very bright
    if v < 45:
        return "black"
    if v > 230 and s < 30:
        return "white"

    # Low saturation greys
    if s < 40 and 60 < v < 230:
        if v < 120:
            return "charcoal"
        return "grey"

    # Hue-based buckets
    h_deg = (h / 179.0) * 360.0

    # Browns / beiges / tans (warm)
    if 20 <= h_deg <= 60:
        if v > 210:
            return "beige"
        if v > 160:
            return "tan"
        if v > 110:
            return "brown"
        return "dark-brown"

    # Greens (olive / deep-green)
    if 60 < h_deg <= 150:
        if v < 150:
            return "olive"
        return "deep-green"

    # Blues (navy / light-blue / pastel-blue)
    if 150 < h_deg <= 260:
        if v < 120:
            return "navy"
        if v > 210:
            return "pastel-blue"
        return "light-blue"

    # Fallbacks
    if v < 120:
        return "charcoal"
    if v > 200:
        return "stone"
    return "brown"

