import logging
from multiprocessing import Process
from boot import scheduler, logger
from libs import process

# 初始化日志配置（假设setup()方法用于配置日志的输出格式、级别等）
logger.setup()

process = process.Manager()


@process.register("scheduler")
def work_scheduler():
    """
    工作函数：启动调度器
    该函数将作为子进程的目标函数执行，负责启动调度器开始工作
    """
    # 启动调度器
    scheduler.start()


if __name__ == "__main__":
    try:
        logging.info("主进程启动，初始化进程管理器...")

        # 启动所有进程
        if process.start_all():
            # 监控进程运行
            process.monitor_all()
        else:
            logging.error("进程启动失败，程序退出")

    except Exception as e:
        logging.error(f"主程序出错: {str(e)}", exc_info=True)
    finally:
        logging.info("主进程退出")
