from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., example="admin")
    password: str = Field(..., example="123456")


class TokenResponse(BaseModel):
    token_type: str = "bearer"
    expires_in: int
    access_token: str
