import logging
import signal
from bootstrap.scheduler import create_scheduler


def handle_shutdown(signum, frame):
    """
    处理系统信号的回调函数，用于优雅关闭调度器

    Args:
        signum: 信号编号
        frame: 当前栈帧
    """
    signal_name = signal.Signals(signum).name
    logging.info(f"接收到 {signal_name} 信号，准备关闭调度器...")
    # 触发主线程的SystemExit，以便执行后续的清理逻辑
    raise SystemExit(0)


if __name__ == "__main__":
    """调度器主启动函数"""
    # 注册系统信号处理器，支持更多优雅关闭的场景
    signal.signal(signal.SIGINT, handle_shutdown)  # 处理Ctrl+C
    signal.signal(signal.SIGTERM, handle_shutdown)  # 处理kill命令

    try:
        logging.info("===== 开始启动定时任务调度器 =====")

        # 创建调度器实例，注册所有任务
        scheduler = create_scheduler()

        # 打印已注册的任务列表，便于验证
        jobs = scheduler.get_jobs()
        if jobs:
            logging.info(f"成功加载 {len(jobs)} 个定时任务:")
            for job in jobs:
                logging.info(f"  - 任务ID: {job.id} | 触发器: {job.trigger}")
        else:
            logging.warning("未发现任何定时任务，请检查任务模块是否正确配置")

        logging.info("调度器启动成功，开始运行任务 (按 Ctrl+C 停止)")
        # 启动调度器（阻塞模式）
        scheduler.start()

    except SystemExit:
        # 正常关闭流程
        logging.info("调度器正在关闭...")
        if 'scheduler' in locals():
            scheduler.shutdown(wait=True)  # 等待当前任务完成后再关闭
            logging.info("调度器已安全关闭")
        logging.info("===== 调度器运行结束 =====")

    except Exception as e:
        # 捕获所有未预期的异常
        logging.error(f"调度器运行过程中发生致命错误: {str(e)}", exc_info=True)
        # 尝试紧急关闭
        if 'scheduler' in locals():
            scheduler.shutdown(wait=False)  # 不等待，立即关闭
        logging.critical("调度器异常退出", exc_info=True)
        exit(1)
