from fastapi import APIRouter, Depends

from app.http import depends
from app.http.depends import get_db
from app.http.user.model import UserDetail
from app.models.user import User

router = APIRouter(prefix="/user")


@router.get("/me", response_model=UserDetail, dependencies=[Depends(get_db)])
def me(user: User = Depends(depends.get_current_user)):
    """
    获取当前登录用户信息

    :param user: 通过依赖注入获取当前用户
    :return: UserDetail 对象
    """
    return UserDetail(
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
    )
