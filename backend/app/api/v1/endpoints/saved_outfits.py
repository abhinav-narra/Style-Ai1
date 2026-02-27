from __future__ import annotations

from typing import Any, List

from fastapi import APIRouter, Depends

from ....core.security import get_current_user
from ....repositories.saved_outfits import SavedOutfitRepository
from ....repositories.user import UserRow
from ...deps import saved_outfit_repo_dep


router = APIRouter()


@router.post("/save-outfit")
async def save_outfit(
    payload: dict[str, Any],
    repo: SavedOutfitRepository = Depends(saved_outfit_repo_dep),
    current_user: UserRow = Depends(get_current_user),
):
    outfit_id = str(payload.get("outfit_id") or payload.get("id") or "")
    if not outfit_id:
        outfit_id = "unknown"
    await repo.add_saved_outfit(current_user.id, outfit_id, payload)
    return {"ok": True}


@router.get("/saved-outfits")
async def list_saved_outfits(
    repo: SavedOutfitRepository = Depends(saved_outfit_repo_dep),
    current_user: UserRow = Depends(get_current_user),
    limit: int = 50,
) -> List[dict[str, Any]]:
    rows = await repo.list_for_user(current_user.id, limit=limit)
    return [
        {
            "id": r.id,
            "user_id": r.user_id,
            "outfit_id": r.outfit_id,
            "created_at": r.created_at,
            "payload": r.payload,
        }
        for r in rows
    ]


@router.delete("/delete-outfit/{outfit_id}")
async def delete_outfit(
    outfit_id: str,
    repo: SavedOutfitRepository = Depends(saved_outfit_repo_dep),
    current_user: UserRow = Depends(get_current_user),
):
    await repo.delete_for_user(current_user.id, outfit_id)
    return {"ok": True}
