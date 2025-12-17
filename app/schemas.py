import html
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime

# --- Auth / User ---
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    email: EmailStr
    @field_validator('username', 'password')
    def sanitize_string(cls, v):
        return html.escape(v) if isinstance(v, str) else v


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expiresAt: datetime


# --- Posts ---
class PostCreate(BaseModel):
    title: str
    content: str
    @field_validator('title', 'content')
    def sanitize_string(cls, v):
        return html.escape(v) if isinstance(v, str) else v


class PostOut(BaseModel):
    id: int
    title: str
    content: str
    author: str

    class Config:
        orm_mode = True
