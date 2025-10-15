import datetime
from typing import Union, Any, Optional
import jwt

from config import setting

# -----------------------------
# JWT 配置
# -----------------------------
SECRET_KEY = setting.SECRET_KEY
ALGORITHM = "HS256"


# -----------------------------
# 生成 JWT Token
# -----------------------------
def encode_token(subject: Union[str, Any], expires_delta: datetime.timedelta = datetime.timedelta(0)) -> str:
    """
    生成 JWT Token。

    - 如果 expires_delta 为 None 或 0，则生成永不过期的 token。
    - 如果 expires_delta > 0，则生成带过期时间的 token。

    Args:
        subject (str | Any): JWT 主题，通常为用户 ID、用户名或其他唯一标识。
        expires_delta (timedelta, optional): token 有效期。默认为 0，表示永不过期。

    Returns:
        str: 加密后的 JWT 字符串。

    Example:
        # 永不过期
        token = encode_token("user123")

        # 一小时后过期
        token = encode_token("user123", timedelta(hours=1))
    """
    to_encode = {"sub": str(subject)}

    # 只有当 expires_delta > 0 时才设置 exp
    if expires_delta is not None and expires_delta.total_seconds() > 0:
        expire = datetime.datetime.now(datetime.UTC) + expires_delta
        to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# -----------------------------
# 解析 JWT Token
# -----------------------------
def decode_token(token: str) -> Optional[Union[str, Any]]:
    """
    解析 JWT Token，返回 payload。

    - 仅解析并返回 token 内部数据，不做过期检查（解码时如果 token 已过期会抛出异常）。
    - payload 中通常包含：
        - sub: 用户唯一标识
        - exp: 过期时间（如果有）

    Args:
        token (str): JWT 字符串。

    Returns:
        dict: JWT payload 字典。

    Raises:
        jose.JWTError: token 无效
        jose.ExpiredSignatureError: token 已过期

    Example:
        payload = decode_token(token)
        user_id = payload["sub"]
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
