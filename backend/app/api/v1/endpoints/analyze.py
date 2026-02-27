from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from ....core.errors import DependencyMissingError, InvalidInputError
from ....models.schemas import AnalyzeResponse
from ....services.stylist import StylistService
from ...deps import stylist_service_dep


router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_image(
    file: UploadFile = File(...),
    stylist: StylistService = Depends(stylist_service_dep),
):
    try:
        raw = await file.read()
        artifacts = await stylist.analyze_image_bytes(raw)
        return artifacts.analyze
    except DependencyMissingError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    except InvalidInputError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

