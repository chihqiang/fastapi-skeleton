from passlib.context import CryptContext

# -----------------------------
# 密码加密上下文
# -----------------------------
# 使用 bcrypt 算法进行哈希
# deprecated="auto" 表示自动弃用旧算法，推荐新算法
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify(plain_password: str, hashed_password: str) -> bool:
    """
    验证明文密码是否与哈希密码匹配

    :param plain_password: 用户输入的明文密码
    :param hashed_password: 数据库中存储的哈希密码
    :return: True 如果匹配，否则 False
    """
    return pwd_context.verify(plain_password, hashed_password)


def make(password: str) -> str:
    """
    将明文密码加密为哈希密码

    :param password: 用户输入的明文密码
    :return: 加密后的哈希密码字符串
    """
    return pwd_context.hash(password)
