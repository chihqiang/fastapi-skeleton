from fastapi import APIRouter, Depends

from app.support import depts
from app.support.depts import get_db
from app.http.user.schemas import UserDetail
from app.models.user import User
from app.support.fast import BaseResponse, JSONSuccess

router = APIRouter(prefix="/user")


@router.get("/me", response_model=BaseResponse[UserDetail], dependencies=[Depends(get_db)])
def me(user: User = Depends(depts.get_current_user)):
    """
    获取当前登录用户信息

    :param user: 通过依赖注入获取当前用户
    :return: UserDetail 对象
    """
    return JSONSuccess(data=UserDetail(
        id=user.id,
        username=user.username,
        nickname=user.nickname,
        gender=user.gender,
        avatar=user.avatar,
        cellphone=user.cellphone,
        email=user.email,
        email_verified_at=user.email_verified_at,
        state=user.state,
        created_at=user.created_at
    ))
