from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ....core.config import Settings
from ....core.security import create_access_token, get_current_user, get_password_hash, verify_password
from ....models.auth import Token, UserBase, UserCreate, UserLogin
from ....repositories.user import UserRepository, UserRow
from ...deps import settings_dep, user_repo_dep


router = APIRouter(prefix="/auth", tags=["auth"])


async def _user_row_to_model(row: UserRow) -> UserBase:
    return UserBase(
        id=row.id,
        email=row.email,
        display_name=row.display_name,
        gender=row.gender,
        created_at=row.created_at,
    )


@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
async def signup(
    payload: UserCreate,
    repo: UserRepository = Depends(user_repo_dep),
    settings: Settings = Depends(settings_dep),
):
    existing = await repo.get_by_email(payload.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user_id = f"user_{uuid.uuid4().hex}"
    password_hash = get_password_hash(payload.password)
    await repo.create_user(
        user_id=user_id,
        email=payload.email,
        password_hash=password_hash,
        display_name=payload.display_name,
        gender=payload.gender,
    )

    access_token = create_access_token({"sub": user_id}, settings=settings)
    return Token(access_token=access_token)


@router.post("/login", response_model=Token)
async def login(
    payload: UserLogin,
    repo: UserRepository = Depends(user_repo_dep),
    settings: Settings = Depends(settings_dep),
):
    user = await repo.get_by_email(payload.email)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    access_token = create_access_token({"sub": user.id}, settings=settings)
    return Token(access_token=access_token)


@router.post("/login-form", response_model=Token, include_in_schema=False)
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    repo: UserRepository = Depends(user_repo_dep),
    settings: Settings = Depends(settings_dep),
):
    user = await repo.get_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    access_token = create_access_token({"sub": user.id}, settings=settings)
    return Token(access_token=access_token)


@router.get("/me", response_model=UserBase)
async def me(current_user: UserRow = Depends(get_current_user)):
    return await _user_row_to_model(current_user)

