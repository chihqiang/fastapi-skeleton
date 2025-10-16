from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.exceptions.exception import AuthenticationError
from app.models.user import User
from base.model import SessionLocal
from libs import crypto
import jwt


def get_db():
    """
    FastAPI 依赖，用于提供 SQLAlchemy Session。
    在请求结束后自动关闭数据库连接。
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
        tokenStr: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
) -> User:
    try:
        payload = crypto.jwt_decode(tokenStr)
    except jwt.ExpiredSignatureError:
        # token 已过期
        raise AuthenticationError(message="Token Expired")
    except jwt.InvalidTokenError:
        # token 无效
        raise AuthenticationError(message="Could not validate credentials")
    except Exception as e:
        # 处理其他未预料到的异常
        raise AuthenticationError(message=f"Token validation failed: {str(e)}")
    user_id = payload.get('sub')
    user = User.undelete(db).filter(User.id == user_id).first()
    if not user:
        raise AuthenticationError(message="User not found")
    if not user.is_enabled():
        raise AuthenticationError(message='Inactive user')
    return user
