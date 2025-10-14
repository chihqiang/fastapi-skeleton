import os
from pathlib import Path

# -----------------------------
# 项目根目录
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------
# 数据库配置
# -----------------------------
# SQLite 数据库路径
DATABASE_URL = "sqlite:///" + os.path.join(BASE_DIR, "storage", "db.sqlite3")

# 设置日志级别为 INFO，表示会记录 INFO、WARNING、ERROR、CRITICAL 级别的日志信息
LOG_LEVEL = "INFO"
# 设置日志文件的保存路径。
# os.path.join 用于拼接路径，BASE_DIR 通常是项目根目录。
# 日志将存放在 BASE_DIR/storage/logs/ 目录下，
# 文件名格式为 fastapi-YYYY-MM-DD.log，其中 {time:YYYY-MM-DD} 表示日期占位符（按天分日志）
LOG_PATH = os.path.join(BASE_DIR, "storage", "logs", "fastapi-{time:YYYY-MM-DD}.log")
# 设置日志保留时间为 14 天，超过这个时间的日志文件会被自动删除（由日志系统控制）
LOG_RETENTION = "14 days"

# -----------------------------
# JWT 配置
# -----------------------------

# JWT 加密密钥（Secret Key）
# 用于生成和验证 JWT Token 的签名
# ⚠️ 请妥善保管，不要泄露到前端或版本控制系统
# 推荐使用高强度随机字符串，并定期轮换
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
