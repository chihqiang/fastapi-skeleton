import logging
from multiprocessing import Process
from boot import scheduler, logger

# 初始化日志配置（假设setup()方法用于配置日志的输出格式、级别等）
logger.setup()


def work_scheduler():
    """
    工作函数：启动调度器
    该函数将作为子进程的目标函数执行，负责启动调度器开始工作
    """
    # 启动调度器
    scheduler.start()


if __name__ == "__main__":
    # 定义子进程变量，初始初始化置为None
    p1 = None
    try:
        # 记录主进程启动信息，用于监控程序运行状态
        logging.info("主进程启动，创建调度器进程...")

        # 创建子进程，指定目标函数为work_scheduler，进程名为"scheduler"
        p1 = Process(target=work_scheduler, name="scheduler")

        # 启动子进程
        p1.start()

        # 记录子进程启动成功的信息，并输出进程ID（PID）便于系统管理
        logging.info(f"调度器进程已启动，PID: {p1.pid}")

        # 阻塞主进程，等待子进程执行完成
        p1.join()

        # 检查子进程的退出状态码，判断是否正常退出
        if p1.exitcode == 0:
            logging.info("调度器进程正常退出")
        else:
            # 非0退出码通常表示异常退出，记录警告信息
            logging.warning(f"调度器进程异常退出，退出码: {p1.exitcode}")

    # 捕获用户中断信号（如Ctrl+C），优雅处理进程退出
    except KeyboardInterrupt:
        # 判断子进程是否存在且仍在运行
        if p1 and p1.is_alive():
            logging.info("正在终止调度器进程...")
            # 终止子进程
            p1.terminate()
            # 等待子进程终止，设置5秒超时
            p1.join(timeout=5)
            # 如果超时后子进程仍未终止，记录警告信息
            if p1.is_alive():
                logging.warning("调度器进程未能正常终止，可能需要强制结束")

    # 捕获其他未预料到的异常，确保程序稳定退出
    except Exception as e:
        # 记录异常详情，包括堆栈信息，便于问题排查
        logging.error(f"主进程出错: {str(e)}", exc_info=True)
        # 如果子进程仍在运行，终止它
        if p1 and p1.is_alive():
            p1.terminate()

    # 无论程序正常结束还是异常退出，都会执行的代码块
    finally:
        logging.info("主进程退出")