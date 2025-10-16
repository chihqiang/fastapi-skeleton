import datetime
from typing import Union, Any, Optional
import jwt

from config import setting

# -----------------------------
# JWT 核心配置
# -----------------------------
SECRET_KEY = setting.SECRET_KEY
ALGORITHM = "HS256"


# -----------------------------
# 生成 JWT Token
# -----------------------------
def encode_token(subject: Union[str, Any], expires_delta: datetime.timedelta = datetime.timedelta(0)) -> str:
    """
    生成JSON Web Token (JWT)

    功能描述：
        根据提供的主题信息和有效期，生成加密的JWT令牌。
        令牌包含主题标识，可选包含过期时间戳用于自动失效控制。

    参数说明：
        subject: 令牌主题信息，通常为用户ID、用户名等唯一标识
                 支持字符串或可转换为字符串的任意类型
        expires_delta: 令牌有效期，默认值为0表示永不过期
                      传入正的时间间隔则令牌会在指定时间后失效

    返回值：
        加密后的JWT字符串

    使用示例：
        # 生成永不过期的令牌
        permanent_token = encode_token("user_1001")

        # 生成30分钟后过期的令牌
        temporary_token = encode_token("user_1001", datetime.timedelta(minutes=30))
    """
    to_encode = {"sub": str(subject)}

    if expires_delta is not None and expires_delta.total_seconds() > 0:
        expire = datetime.datetime.now(datetime.UTC) + expires_delta
        to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# -----------------------------
# 解析 JWT Token
# -----------------------------
def decode_token(token: str) -> Optional[Union[str, Any]]:
    """
    解析JWT令牌，提取负载数据

    功能描述：
        对JWT令牌进行解密和验证，返回其中包含的负载信息。
        内部会自动验证令牌签名有效性，若令牌已过期会抛出相应异常。

    参数说明：
        token: 需要解析的JWT字符串

    返回值：
        包含令牌信息的字典，通常包含：
            - sub: 主题信息（用户唯一标识）
            - exp: 过期时间戳（可选，存在于限时令牌中）

    异常说明：
        jwt.ExpiredSignatureError: 令牌已过期（exp时间戳早于当前时间）
        jwt.InvalidTokenError: 令牌无效，包括但不限于以下场景：
            - 签名验证失败（密钥不匹配或令牌被篡改）
            - 令牌格式错误（不符合JWT规范格式）
            - 算法不匹配（使用的解密算法与签名算法不一致）
            - 缺少必要的负载字段（如签名验证所需的字段缺失）
            - 令牌已被吊销（如果系统实现了吊销机制）
            - 无效的时间戳格式（如exp、nbf等时间字段格式错误）

    使用示例：
        try:
            payload = decode_token(auth_token)
            user_id = payload["sub"]  # 提取用户标识
        except jwt.ExpiredSignatureError:
            # 处理令牌过期逻辑
        except jwt.InvalidTokenError:
            # 处理无效令牌逻辑
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])