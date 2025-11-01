from datetime import timedelta

from sqlalchemy.orm import Session

from app.exceptions.exception import AuthenticationError
from app.http.auth.schemas import TokenResponse
from app.models.user import User
from libs import crypto


def loginToken(email: str, password: str, db: Session) -> TokenResponse:
    """
    用户登录核心逻辑，生成 JWT Token。

    步骤：
    1. 根据用户名查询未被软删除的用户。
    2. 验证用户密码是否正确。
    3. 检查用户是否处于启用状态。
    4. 生成 JWT Token 并返回。

    Args:
        email: 邮箱
        password: 密码
        db (Session): SQLAlchemy 数据库会话。

    Returns:
        TokenResponse: 包含 access_token 和有效期（秒）的响应对象。

    Raises:
        AuthenticationError: 用户不存在、密码错误或用户被禁用。
    """
    # 查询未删除用户
    user = User.undelete(db).filter(User.email == email).first()
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
    return TokenResponse(
        access_token=access_token, expires_in=int(expires_delta.total_seconds())
    )
