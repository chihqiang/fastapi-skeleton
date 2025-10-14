from fastapi import APIRouter

from app.http.auth.route import router as authRoute
from app.http.user.route import router as userRoute

api_router = APIRouter()

api_router.include_router(authRoute, tags=["auth"])
api_router.include_router(userRoute, tags=["user"])
