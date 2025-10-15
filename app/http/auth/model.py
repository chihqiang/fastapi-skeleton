from fastapi import Form
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=20, description="用户名长度3-20")
    password: str = Field(..., min_length=6, max_length=50, description="密码长度6-50")


class TokenResponse(BaseModel):
    token_type: str = "bearer"
    expires_in: int
    access_token: str
