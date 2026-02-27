from __future__ import annotations

from fastapi import APIRouter

from .endpoints.analyze import router as analyze_router
from .endpoints.debug import router as debug_router
from .endpoints.health import router as health_router
from .endpoints.history import router as history_router
from .endpoints.auth import router as auth_router
from .endpoints.saved_outfits import router as saved_outfits_router
from .endpoints.recommend import router as recommend_router
from .endpoints.chat import router as chat_router


router = APIRouter(prefix="/v1")
router.include_router(health_router, tags=["health"])
router.include_router(analyze_router, tags=["vision"])
router.include_router(debug_router, tags=["vision-debug"])
router.include_router(recommend_router, tags=["stylist"])
router.include_router(history_router, tags=["history"])
router.include_router(auth_router, tags=["auth"])
router.include_router(saved_outfits_router, tags=["stylist"])
router.include_router(chat_router, tags=["chat"])

