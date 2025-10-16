import logging

from apscheduler.schedulers.blocking import BlockingScheduler
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
    logging.info("BlockingScheduler initializing")
    # 返回调度器实例，外部可调用 start() 启动
    return scheduler


def start():
    """调度器主启动函数"""
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
