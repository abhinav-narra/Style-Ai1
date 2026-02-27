from __future__ import annotations

import base64
import io
from typing import Any

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

