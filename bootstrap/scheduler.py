import importlib
import logging
import pkgutil
from apscheduler.schedulers.blocking import BlockingScheduler
from app.providers import logging_provider
import app.crontab
# 全局调度器实例，所有任务装饰器会使用它注册任务
scheduler = BlockingScheduler()


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

    # 自动扫描并注册 app.jobs 下的所有任务模块
    register_job()

    # 返回调度器实例，外部可调用 start() 启动
    return scheduler


def register_job():
    """
    自动扫描 app.jobs 包下的所有模块并导入

    逻辑说明：
    1. 遍历 app.jobs 包下的所有模块（不包含子包）
    2. 动态导入每个模块
       - 导入模块后，模块内使用 @crontab.scheduled_job 装饰器的任务会自动注册到全局 crontab
    3. 打印日志，表示任务全部注册完成
    """
    # 遍历 app.jobs 包下的所有模块
    for loader, module_name, is_pkg in pkgutil.iter_modules(app.crontab.__path__):
        # 动态导入模块
        importlib.import_module(f"app.crontab.{module_name}")

    logging.info("All jobs registered")
