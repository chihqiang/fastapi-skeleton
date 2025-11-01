from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserDetail(BaseModel):
    id: int
    email: Optional[str]
    email_verified_at: Optional[datetime]
    state: str
    created_at: datetime
