from sqlalchemy import Column, DateTime, Integer, String

from app.models import BaseModelWithSoftDelete


class User(BaseModelWithSoftDelete):
    """
    用户模型
    表示系统中的用户信息。
    继承 BaseModelWithSoftDelete，实现软删除功能（deleted_at 字段）。
    """

    __tablename__ = "users"  # 数据库表名
    __table_args__ = {"comment": "用户表"}  # 表描述

    # -----------------------------
    # 字段定义
    # -----------------------------
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键，自增ID")
    username = Column(
        String(255), unique=True, nullable=False, comment="用户名，唯一，必填"
    )
    password = Column(String(255), nullable=False, comment="密码哈希，bcrypt 加密")
    cellphone = Column(
        String(50), unique=True, nullable=False, comment="手机号，唯一，必填"
    )
    email = Column(String(255), unique=True, nullable=False, comment="邮箱，唯一，必填")
    email_verified_at = Column(DateTime, nullable=True, comment="邮箱验证时间")
    state = Column(
        String(50),
        default="enabled",
        nullable=False,
        comment="用户状态，enabled 表示启用",
    )
    nickname = Column(String(100), nullable=False, comment="昵称")
    gender = Column(
        String(50),
        default="unknown",
        nullable=False,
        comment="性别，unknown 表示未指定",
    )
    avatar = Column(String(255), nullable=True, comment="头像 URL")

    # -----------------------------
    # 实例方法
    # -----------------------------
    def is_enabled(self) -> bool:
        """
        判断用户是否处于启用状态。
        :return: True 如果 state 为 'enabled'，否则 False
        """
        return self.state == "enabled"
