import asyncio
import logging
import signal
from typing import Optional

from boot.scheduler import create_app
from boot.setup import logger

# ==========================
# 日志初始化
# ==========================
logger.setup()
logging.info("===== 开始启动定时任务调度器 =====")

app = create_app()


async def shutdown(signal_name: Optional[str] = None):
    """优雅关闭调度器"""
    if signal_name:
        logging.info(f"收到系统信号 {signal_name}，正在关闭调度器...")
    else:
        logging.info("收到退出请求，正在关闭调度器...")
    try:
        shutdown_method = app.shutdown
        if asyncio.iscoroutinefunction(shutdown_method):
            await app.shutdown(wait=True)
        else:
            app.shutdown(wait=True)
        logging.info("调度器已优雅关闭。")
    except Exception as e:
        logging.error(f"关闭调度器时出错: {e}", exc_info=True)
    finally:
        logging.info("===== 调度器已完全退出 =====")


async def main():
    """主异步函数：启动调度器并保持运行"""
    try:
        start_method = app.start
        if asyncio.iscoroutinefunction(start_method):
            await app.start()
        else:
            app.start()
        logging.info("调度器启动成功，开始运行任务...")
        # 注册系统信号（Ctrl+C / SIGTERM）
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(
                sig, lambda s=sig: asyncio.create_task(shutdown(s.name))
            )
        # 保持事件循环运行
        await asyncio.Event().wait()
    except asyncio.CancelledError:
        pass
    except KeyboardInterrupt:
        logging.info("用户中断操作，正在关闭调度器...")
        await shutdown("KeyboardInterrupt")
    except Exception as e:
        logging.error(f"调度器运行异常: {e}", exc_info=True)
        shutdown_method = app.shutdown
        if asyncio.iscoroutinefunction(shutdown_method):
            await app.shutdown(wait=False)
        else:
            app.shutdown(wait=False)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("检测到 KeyboardInterrupt，程序退出。")
    except RuntimeError as e:
        if "Event loop is closed" not in str(e):
            logging.critical(f"致命错误: {e}", exc_info=True)
    finally:
        logging.info("===== 调度器主程序退出 =====")
