import logging
import os

from boot.celery import create_app
from boot.setup import logger

logger.setup()

app = create_app()

if __name__ == "__main__":
    cpu_count = os.cpu_count() or 4  # 获取CPU核心数，默认4核
    concurrency = min(cpu_count, 8)  # 限制最大并发数为8，可按需调整
    try:
        app.worker_main([
            'worker',
            f'--concurrency={concurrency}',
            '--max-tasks-per-child=100'  # 每个子进程最多处理100个任务后重启
        ])
    except KeyboardInterrupt:
        # 捕获Ctrl+C手动终止信号，友好退出
        logging.warning("接收到手动终止信号，Celery Worker正在停止")
    except Exception as e:
        # 捕获所有未预期异常，打印详细日志后退出
        logging.error(f"Celery Worker启动失败，异常信息：{str(e)}", exc_info=True)
