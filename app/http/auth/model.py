from fastapi import Form
from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    token_type: str = "bearer"
    expires_in: int
    access_token: str
