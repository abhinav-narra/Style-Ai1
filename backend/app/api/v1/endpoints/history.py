from __future__ import annotations

from fastapi import APIRouter, Depends

from ....models.schemas import HistoryEntry, HistoryResponse
from ....repositories.history import HistoryRepository
from ....repositories.user import UserRow
from ....core.security import get_current_user
from ...deps import history_repo_dep


router = APIRouter()


@router.get("/history/{user_id}", response_model=HistoryResponse, include_in_schema=False)
async def history_debug(user_id: str, limit: int = 50, repo: HistoryRepository = Depends(history_repo_dep)):
    rows = await repo.list_recent(user_id, limit=limit)
    entries = [
        HistoryEntry(user_id=r.user_id, outfit_id=r.outfit_id, created_at=r.created_at, payload=r.payload)
        for r in rows
    ]
    return HistoryResponse(user_id=user_id, entries=entries)


@router.get("/history", response_model=HistoryResponse)
async def history_me(
    limit: int = 50,
    repo: HistoryRepository = Depends(history_repo_dep),
    current_user: UserRow = Depends(get_current_user),
):
    rows = await repo.list_recent(current_user.id, limit=limit)
    entries = [
        HistoryEntry(user_id=r.user_id, outfit_id=r.outfit_id, created_at=r.created_at, payload=r.payload)
        for r in rows
    ]
    return HistoryResponse(user_id=current_user.id, entries=entries)

