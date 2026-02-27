from __future__ import annotations

from fastapi import Request

from ..core.config import Settings, get_settings
from ..repositories.history import HistoryRepository
from ..services.stylist import StylistService


def settings_dep() -> Settings:
    return get_settings()


def history_repo_dep(request: Request) -> HistoryRepository:
    return request.app.state.history_repo  # type: ignore[attr-defined]


def stylist_service_dep(request: Request) -> StylistService:
    return request.app.state.stylist  # type: ignore[attr-defined]

