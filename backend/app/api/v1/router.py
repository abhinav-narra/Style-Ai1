from __future__ import annotations

from fastapi import APIRouter

from .endpoints.analyze import router as analyze_router
from .endpoints.debug import router as debug_router
from .endpoints.health import router as health_router
from .endpoints.history import router as history_router
from .endpoints.recommend import router as recommend_router


router = APIRouter(prefix="/v1")
router.include_router(health_router, tags=["health"])
router.include_router(analyze_router, tags=["vision"])
router.include_router(debug_router, tags=["vision-debug"])
router.include_router(recommend_router, tags=["stylist"])
router.include_router(history_router, tags=["history"])

