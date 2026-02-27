from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from ....core.errors import DependencyMissingError, InvalidInputError
from ....models.schemas import RecommendRequest, RecommendResponse
from ....services.stylist import StylistService
from ....utils.json_safe import safe_json_loads, safe_parse_model
from ...deps import stylist_service_dep


router = APIRouter()


@router.post("/recommend", response_model=RecommendResponse)
async def recommend(
    request_json: str = Form(..., description="JSON for RecommendRequest"),
    image: UploadFile | None = File(default=None),
    stylist: StylistService = Depends(stylist_service_dep),
):
    parsed = safe_json_loads(request_json)
    if not parsed.ok:
        raise HTTPException(status_code=400, detail=parsed.error)

    model, err = safe_parse_model(parsed.value, RecommendRequest)
    if err or model is None:
        raise HTTPException(status_code=400, detail=f"Invalid request: {err}")

    image_bytes = await image.read() if image else None

    try:
        return await stylist.recommend(model, image_bytes=image_bytes)
    except DependencyMissingError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    except InvalidInputError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

