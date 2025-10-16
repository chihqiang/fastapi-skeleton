import importlib
import logging
import pkgutil
from apscheduler.schedulers.blocking import BlockingScheduler
from app.providers import logging_provider
import app.crontab
from config import setting
from libs.register import package_modules

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
    """注册app.crontab包下的所有模块并输出日志"""
    package_name = setting.CRONTAB_PACKAGE_NAME
    success_count, failed_modules = package_modules(package_name)

    # 输出汇总日志
    if not failed_modules:
        logging.info(f"✅ 成功导入 {package_name} 包下所有模块，共 {success_count} 个")
    else:
        logging.warning(
            f"⚠️ {package_name} 包模块导入完成 - "
            f"成功: {success_count} 个, 失败: {len(failed_modules)} 个"
        )
        # 详细输出失败模块信息
        for idx, error in enumerate(failed_modules, 1):
            logging.warning(f"  失败项 {idx}: {error}")

    # 特殊情况提示：成功导入模块但数量为0
    if success_count == 0 and not failed_modules:
        logging.info(f"ℹ️ {package_name} 包下未发现任何可导入的模块")
