import logging
import signal

from apscheduler.schedulers.blocking import BlockingScheduler
from app.providers import logging_provider
from config import setting
from libs.modules import auto_import_modules

# 全局调度器实例，所有任务装饰器会使用它注册任务
scheduler = BlockingScheduler()


@auto_import_modules(package_name=setting.CRONTAB_PACKAGE_NAME)
def create_scheduler() -> BlockingScheduler:
    """
    创建并初始化调度器

    1. 初始化日志
    2. 自动注册任务模块
    3. 返回调度器实例

    Returns:
        BlockingScheduler: 已注册所有任务的调度器实例
    """
    # 初始化日志系统，例如设置日志格式、级别等
    logging_provider.register()
    logging.info("BlockingScheduler initializing")
    # 返回调度器实例，外部可调用 start() 启动
    return scheduler


def start():
    """调度器主启动函数"""
    # 注册系统信号处理器，支持更多优雅关闭的场景
    signal.signal(signal.SIGINT, handle_shutdown)  # 处理Ctrl+C
    signal.signal(signal.SIGTERM, handle_shutdown)  # 处理kill命令

    logging.info("===== 开始启动定时任务调度器 =====")

    # 创建调度器实例，注册所有任务
    scheduler_app = create_scheduler()
    try:
        # 打印已注册的任务列表，便于验证
        jobs = scheduler_app.get_jobs()
        if jobs:
            logging.info(f"成功加载 {len(jobs)} 个定时任务:")
            for job in jobs:
                logging.info(f"  - 任务ID: {job.id} | 触发器: {job.trigger}")
        else:
            logging.warning("未发现任何定时任务，请检查任务模块是否正确配置")

        logging.info("调度器启动成功，开始运行任务 (按 Ctrl+C 停止)")
        # 启动调度器（阻塞模式）
        scheduler_app.start()

    except SystemExit:
        # 正常关闭流程
        logging.info("调度器正在关闭...")
        if 'scheduler' in locals():
            scheduler_app.shutdown(wait=True)  # 等待当前任务完成后再关闭
            logging.info("调度器已安全关闭")
        logging.info("===== 调度器运行结束 =====")

    except Exception as e:
        # 捕获所有未预期的异常
        logging.error(f"调度器运行过程中发生致命错误: {str(e)}", exc_info=True)
        # 尝试紧急关闭
        if 'scheduler' in locals():
            scheduler_app.shutdown(wait=False)  # 不等待，立即关闭
        logging.critical("调度器异常退出", exc_info=True)


def handle_shutdown(signum, frame):
    """
    处理系统信号的回调函数，用于优雅关闭调度器

    Args:
        signum: 信号编号
        frame: 当前栈帧
    """
    signal_name = signal.Signals(signum).name
    logging.info(f"接收到 {signal_name} 信号，准备关闭调度器...")
