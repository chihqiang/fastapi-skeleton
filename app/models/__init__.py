from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, create_engine, pool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, Session, mapped_column, sessionmaker

from config import setting

# -----------------------------
# 声明基础 ORM 类
# -----------------------------
Base = declarative_base()

connect_args = (
    {"check_same_thread": False} if setting.DATABASE_URL.startswith("sqlite") else {}
)

# 创建数据库引擎
engine = create_engine(
    setting.DATABASE_URL,
    poolclass=pool.NullPool,
    connect_args=connect_args,
    echo=True,  # 打印 SQL 日志，可选
)
# 创建 Session 工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# -----------------------------
# 基础模型
# -----------------------------
class BaseModel(Base):
    """
    基础模型类，提供创建时间和更新时间字段。
    该类为抽象类，不会在数据库中创建表。
    """

    __abstract__ = True  # 不会创建单独的表

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, comment="主键ID"
    )
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now, onupdate=datetime.now, comment="更新时间"
    )


# -----------------------------
# 带软删除功能的模型
# -----------------------------
class BaseModelWithSoftDelete(BaseModel):
    """
    带软删除功能的基础模型。
    继承自 BaseModel，增加 deleted_at 字段。
    """

    __abstract__ = True  # 抽象类，不会直接创建表

    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(), nullable=True, default=None, comment="删除时间"
    )

    # -----------------------------
    # 类方法
    # -----------------------------
    @classmethod
    def undelete(cls, db: Session):
        # 返回 Query 对象，而不是列表
        return db.query(cls).filter(cls.deleted_at.is_(None))
