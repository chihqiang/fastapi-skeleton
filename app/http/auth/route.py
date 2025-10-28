from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.http.auth import service
from app.support import depts
from app.http.auth.schemas import TokenResponse, LoginRequest
from app.support.fast import BaseResponse, JSONSuccess

router = APIRouter(prefix="/auth")


@router.post("/login", response_model=BaseResponse[TokenResponse])
async def login(request: LoginRequest, db: Session = Depends(depts.get_db)):
    return JSONSuccess(data=service.loginToken(request.username, request.password, db))
