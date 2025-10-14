import logging
import sys
from loguru import logger

from config import setting


def register(app=None):
    """
    注册日志系统，统一接管 Python logging 与 Loguru 的日志输出。
    可在 FastAPI 启动时调用，例如：
        from common.log import register
        register(app)
    """
    # 从配置中读取日志级别、路径和保留时间
    level = setting.LOG_LEVEL           # 日志级别，例如 "INFO"、"DEBUG"
    path = setting.LOG_PATH             # 日志文件保存路径，如 "storage/logs/fastapi-{time:YYYY-MM-DD}.log"
    retention = setting.LOG_RETENTION   # 日志保留时间，例如 "14 days"

    # 拦截所有标准 logging 模块的日志，交由 Loguru 统一处理
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(level)

    # 移除其他 logger 的独立 handlers，
    # 让所有日志都向上冒泡到 root logger，由 Loguru 统一输出
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    # 配置 Loguru 的输出方式
    logger.configure(handlers=[
        # 控制台输出日志（stdout）
        {"sink": sys.stdout},
        # 文件输出日志，每天凌晨 00:00 自动轮转日志文件，
        # 并保留指定天数后自动清理旧日志
        {"sink": path, "rotation": "00:00", "retention": retention},
    ])


class InterceptHandler(logging.Handler):
    """
    该类用于拦截 Python 原生 logging 的日志消息，
    并将其转发给 Loguru，确保所有日志系统统一格式与输出。
    """
    def emit(self, record):
        """
        emit() 方法在每次 logging 记录日志时被调用，
        record 对象包含日志的详细信息。
        """
        # 尝试匹配 Loguru 的日志级别名称
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            # 如果不存在对应级别，则直接使用数值级别
            level = record.levelno

        # 找到日志实际调用的位置（而不是 logging 内部函数）
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        # 使用 Loguru 输出日志，保持原有异常信息和调用层级
        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())
