from pydantic import BaseModel


class TokenResponse(BaseModel):
    token_type: str = "bearer"
    expires_in: int
    access_token: str
