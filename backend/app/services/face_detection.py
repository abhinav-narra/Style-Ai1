from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..core.errors import DependencyMissingError
from ..models.schemas import FaceBox


@dataclass(frozen=True)
class FaceDetectionResult:
    faces: list[FaceBox]


class FaceDetector:
    """
    OpenCV Haar-cascade face detector (lazy-imported).
    """

    def __init__(self, min_confidence: float = 0.5):
        # min_confidence is mapped to Haar cascade minNeighbors / scaleFactor heuristically.
        self._min_confidence = float(min_confidence)

    def detect(self, bgr_image) -> FaceDetectionResult:
        cv2 = _require_cv2()

        height, width = int(bgr_image.shape[0]), int(bgr_image.shape[1])
        if height == 0 or width == 0:
            return FaceDetectionResult(faces=[])

        gray = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)

        cascade_path = getattr(cv2.data, "haarcascades", "") + "haarcascade_frontalface_default.xml"
        if not cascade_path:
            raise DependencyMissingError(
                "opencv-data",
                "OpenCV haarcascade data not found; ensure opencv-python is installed correctly.",
            )

        classifier = cv2.CascadeClassifier(cascade_path)
        if classifier.empty():
            raise DependencyMissingError(
                "opencv-data",
                "Failed to load Haar cascade; check your OpenCV installation.",
            )

        # Heuristic mapping: higher min_confidence -> stricter detection parameters.
        scale_factor = 1.1
        min_neighbors = 5
        if self._min_confidence >= 0.7:
            min_neighbors = 7
        elif self._min_confidence <= 0.3:
            min_neighbors = 3

        detections = classifier.detectMultiScale(
            gray,
            scaleFactor=scale_factor,
            minNeighbors=min_neighbors,
            flags=cv2.CASCADE_SCALE_IMAGE,
            minSize=(32, 32),
        )

        faces: list[FaceBox] = []
        for (x, y, w, h) in detections:
            if w <= 0 or h <= 0:
                continue
            # Haar cascade does not give probability; we expose a fixed high confidence for now.
            faces.append(FaceBox(x=int(x), y=int(y), w=int(w), h=int(h), confidence=0.9))

        # Sort largest face first (more stable for selfies)
        faces.sort(key=lambda f: f.w * f.h, reverse=True)
        return FaceDetectionResult(faces=faces)


def _require_cv2() -> Any:
    try:
        import cv2  # type: ignore
    except ModuleNotFoundError as e:
        raise DependencyMissingError("opencv-python", "Install backend/requirements.txt for face detection") from e
    return cv2

