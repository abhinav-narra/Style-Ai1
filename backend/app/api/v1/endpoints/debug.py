from __future__ import annotations

import io

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import Response

from ....core.errors import DependencyMissingError, InvalidInputError
from ....services.stylist import StylistService
from ....utils.images import decode_image_bytes_to_bgr
from ...deps import stylist_service_dep


router = APIRouter()


@router.post("/debug/boxes", summary="Debug: visualize detected face boxes")
async def debug_boxes(
    file: UploadFile = File(...),
    stylist: StylistService = Depends(stylist_service_dep),
):
    """
    Debug helper that draws detected face bounding boxes on the uploaded image
    and returns a JPEG image. Not intended for end users.
    """
    try:
        raw = await file.read()
        # Reuse the same decoding path used elsewhere.
        bgr = decode_image_bytes_to_bgr(raw)

        # Reuse the shared face detector so behavior matches /analyze.
        det = stylist._faces.detect(bgr)  # type: ignore[attr-defined]

        try:
            import cv2  # type: ignore
        except ModuleNotFoundError as e:
            raise DependencyMissingError("opencv-python", "Install backend/requirements.txt for debug/boxes") from e

        for face in det.faces:
            x, y, w, h = face.x, face.y, face.w, face.h
            cv2.rectangle(bgr, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Encode back to JPEG for response.
        ok, buf = cv2.imencode(".jpg", bgr)
        if not ok:
            raise InvalidInputError("Failed to encode debug image")
        data = buf.tobytes()
        return Response(content=data, media_type="image/jpeg")
    except DependencyMissingError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    except InvalidInputError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

