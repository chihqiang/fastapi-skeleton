import logging

from boot.scheduler import creat_app
from boot.setup import logger

logger.setup()
app = creat_app()

if __name__ == "__main__":
    """调度器主启动函数"""
    logging.info("===== 开始启动定时任务调度器 =====")
    try:
        # 启动调度器
        app.start()
    except KeyboardInterrupt:
        # 专门处理用户按下Ctrl+C的情况
        logging.info("用户中断操作，正在关闭调度器...")
        # 优雅地关闭调度器，等待正在执行的任务完成
        app.shutdown(wait=True)
        logging.info("调度器已成功关闭")
    except Exception as e:
        # 捕获所有未预期的异常
        logging.error(f"调度器运行过程中发生致命错误: {str(e)}", exc_info=True)
        # 尝试紧急关闭
        app.shutdown(wait=False)  # 不等待，立即关闭
        logging.critical("调度器异常退出", exc_info=True)
