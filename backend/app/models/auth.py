from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserBase(BaseModel):
    id: str = Field(..., min_length=1, max_length=128)
    email: EmailStr
    display_name: str | None = None
    gender: str | None = None
    created_at: datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    display_name: str | None = None
    gender: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str

