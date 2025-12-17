from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# --- Auth / User ---
class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr


class TokenResponse(BaseModel):
    token: str
    expiresAt: datetime


# --- Posts ---
class PostCreate(BaseModel):
    title: str
    content: str


class PostOut(BaseModel):
    id: int
    title: str
    content: str
    author: str

    class Config:
        orm_mode = True
