from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models import BaseModelWithSoftDelete


class User(BaseModelWithSoftDelete):
    """
    用户模型
    表示系统中的用户信息，支持软删除和 JSON 序列化。
    """

    __tablename__ = "users"
    __table_args__ = {"comment": "用户表"}
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, comment="邮箱"
    )
    email_verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(), nullable=True, comment="邮箱验证时间"
    )
    password: Mapped[str] = mapped_column(String(255), nullable=False, comment="密码")
    state: Mapped[str] = mapped_column(
        String(50),
        default="enabled",
        nullable=False,
        comment="用户状态，enabled 表示启用",
    )

    # 实例方法
    def is_enabled(self) -> bool:
        return self.state == "enabled"
