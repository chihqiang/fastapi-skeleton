from datetime import timedelta

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.exceptions.exception import AuthenticationError
from app.http import depends
from app.http.auth.model import TokenResponse
from app.models.user import User
from libs import crypto

router = APIRouter(prefix="/auth")


@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(depends.get_db)):
    return loginToken(form_data.username, form_data.password, db)


def loginToken(username: str, password: str, db: Session) -> TokenResponse:
    """
    用户登录核心逻辑，生成 JWT Token。

    步骤：
    1. 根据用户名查询未被软删除的用户。
    2. 验证用户密码是否正确。
    3. 检查用户是否处于启用状态。
    4. 生成 JWT Token 并返回。

    Args:
        username: 用户名
        password: 密码
        db (Session): SQLAlchemy 数据库会话。

    Returns:
        TokenResponse: 包含 access_token 和有效期（秒）的响应对象。

    Raises:
        AuthenticationError: 用户不存在、密码错误或用户被禁用。
    """
    # 查询未删除用户
    user = User.undelete(db).filter(User.username == username).first()

    # 验证密码
    if not user or not crypto.hash_verify(password, user.password):
        raise AuthenticationError("用户名或密码错误")

    # 检查用户是否启用
    if not user.is_enabled():
        raise AuthenticationError("用户已被禁用")

    # 设置 token 有效期（3 小时）
    expires_delta = timedelta(hours=3)

    # 生成 JWT Token
    access_token = crypto.jwt_encode(user.id, expires_delta)

    # 返回 Token 响应
    return TokenResponse(
        access_token=access_token,
        expires_in=int(expires_delta.total_seconds())
    )
