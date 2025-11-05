import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# 项目核心路径配置
# -----------------------------
# 项目根目录路径：定位项目最顶层目录，作为所有子路径（如存储、日志）的基准
# Path(__file__)：当前配置文件的绝对路径
# resolve()：处理路径中的符号链接，返回真实绝对路径
# parent.parent：向上两级目录（假设当前文件在"项目根目录/config/"下，此操作定位到项目根目录）
BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------
# 数据库配置（SQLite）
# -----------------------------
# SQLite数据库文件的完整路径：指定数据库文件的存储位置
# os.path.join：跨平台路径拼接（避免Windows/Linux路径分隔符差异）
# storage/db.sqlite3：数据库文件存放在项目根目录下的"storage"目录，文件名为"db.sqlite3"
# 若后续切换数据库（如MySQL），可在此处修改为对应连接URL（如"mysql+pymysql://user:pass@host:port/db"）
DATABASE_URL = os.getenv(
    "DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "storage", "db.sqlite3")
)

# -----------------------------
# 日志系统配置
# 控制日志的输出级别、存储路径和文件生命周期，便于问题排查和系统监控
# -----------------------------
# 日志输出级别：定义日志系统需要记录的日志严重程度
# 级别优先级（从低到高）：DEBUG < INFO < WARNING < ERROR < CRITICAL
# 设置为"INFO"时，会记录 INFO 及以上级别日志（忽略 DEBUG 级别的调试信息）
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# 日志文件存储路径：指定日志文件的生成位置和命名规则
# storage/logs/：日志文件存放在项目根目录下的"storage/logs"目录（需确保目录已创建，避免报错）
# fastapi-{time:YYYY-MM-DD}.log：日志文件按日期命名（如"fastapi-2025-10-16.log"）
# {time:YYYY-MM-DD}：日志系统的日期占位符，实现"按天分日志"，便于按时间筛选日志文件
LOG_PATH = os.path.join(BASE_DIR, "storage", "logs", "fastapi-{time:YYYY-MM-DD}.log")

# 日志文件保留时间：控制旧日志的自动清理策略，避免磁盘空间占用过大
# 设置为"14 days"时，日志系统会自动删除14天前的日志文件
# 支持的单位：days（天）、hours（小时）、minutes（分钟），需配合数值使用
LOG_RETENTION = "14 days"

# -----------------------------
# JWT（JSON Web Token）认证配置
# 用于API接口的身份验证，确保请求来源合法
# -----------------------------
# JWT签名密钥：生成和验证JWT Token的核心密钥，决定Token的安全性
# 作用：Token生成时用此密钥签名，验证时用此密钥验签，防止Token被篡改
# ⚠️ 安全警告：
# 1. 生产环境必须使用高强度随机字符串（推荐32位以上，可通过"openssl rand -hex 32"生成）
# 2. 禁止将密钥泄露到前端代码、公开仓库（如GitHub）或配置文件备份中
# 3. 建议定期轮换密钥（轮换时需处理旧Token的平滑过渡，避免用户强制登出）
SECRET_KEY = os.getenv(
    "SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
)

# -----------------------------
# 定时任务（Crontab）配置
# -----------------------------
# 说明：
# 此配置用于指定定时任务模块的扫描根包，
# 关联定时任务注册逻辑（如自动扫描并注册模块内的定时任务）。
# 被扫描的包下所有模块都将被导入并注册任务。

# 定时任务模块根包名
# 作用：指定包含定时任务定义的Python包路径。
# 示例：若定时任务定义在 "app/crontab" 下的各个模块中，则设置为 "app.crontab"。
# 注意：
#   1. 所有定时任务模块必须放在此包下，才能被注册逻辑扫描到。
#   2. 如果有子包且希望递归扫描，需要在扫描逻辑中开启子包扫描配置。
#   3. 修改此变量可更换定时任务模块路径，无需改动注册函数逻辑。
CRONTAB_PACKAGE_NAME = "app.tasks.crontab"

# 业务任务模块根包名
# 作用：指定包含普通业务任务模块的Python包路径，可用于定时或异步任务注册。
# 示例：若业务任务定义在 "app/jobs" 下的各个模块中，则设置为 "app.jobs"。
# 注意：
#   1. 同样支持递归扫描子包（需在扫描逻辑中配置）。
#   2. 修改此变量可更换业务任务模块路径，无需改动注册函数逻辑。
JOB_PACKAGE_NAME = "app.tasks.jobs"

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
REDIS_DB = os.getenv("REDIS_DB", 0)
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
CACHE_CFG = {
    "type": "memory",
    "redis": {
        "host": REDIS_HOST,
        "port": REDIS_PORT,
        "db": REDIS_DB,
        "password": REDIS_PASSWORD,
        "max_connections": 10,
        "decode_responses": False,
    },
    "memory": {"max_size": 1000},
}
