from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.http.auth import service
from app.support import depts
from app.http.auth.schemas import LoginRequest
from app.support.fast import JSONSuccess

router = APIRouter(prefix="/auth")


@router.post("/login")
async def login(request: LoginRequest, db: Session = Depends(depts.get_db)):
    return JSONSuccess(data=service.loginToken(request.username, request.password, db))
