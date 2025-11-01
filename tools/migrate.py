import logging
import os
import sys

from app.models import Base, SessionLocal, engine
from app.models.user import User
from libs import crypto

# 获取当前文件所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录（当前目录的上级目录）
project_root = os.path.dirname(current_dir)
# 添加项目根目录到模块搜索路径
sys.path.insert(0, project_root)

# -----------------------------
# 配置日志
# -----------------------------
logging.basicConfig(level=logging.DEBUG)


def create_tables():
    """创建所有数据库表"""
    logging.info("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    logging.info("数据库表创建完成！")


def create_default_admin():
    """创建默认管理员"""
    db = SessionLocal()
    try:
        # 检查管理员是否存在
        admin = db.query(User).filter(User.email == "admin@example.com").first()
        if admin:
            logging.info("🔹 默认管理员已存在，跳过创建。")
            return

        # 创建管理员
        admin_user = User(
            email="admin@example.com",
            password=crypto.hash_make("123456"),
            state="enabled",
        )
        db.add(admin_user)
        db.commit()
        logging.info("默认管理员创建成功！用户名：admin，密码：123456")
    except Exception as e:
        db.rollback()
        logging.error(f"创建默认管理员失败: {e}")
    finally:
        db.close()


# -----------------------------
# 主程序
# -----------------------------
if __name__ == "__main__":
    create_tables()
    create_default_admin()
