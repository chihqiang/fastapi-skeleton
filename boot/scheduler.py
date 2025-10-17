import logging

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.blocking import BlockingScheduler
from config import setting
from libs import modules

# 全局调度器实例，所有任务装饰器会使用它注册任务
blocking = BlockingScheduler(
    jobstores={
        "default": SQLAlchemyJobStore(url=setting.DATABASE_URL),
    },
    # 时区配置（优先使用项目配置，默认UTC）
    timezone=getattr(setting, 'TIMEZONE', 'UTC'),
    # 任务默认参数（统一控制任务行为）
    job_defaults={
        'coalesce': True,  # 合并错过的重复任务（避免任务堆积）
        'max_instances': 3,  # 同一任务最大并发实例数
        'misfire_grace_time': 30  # 任务误触发容忍时间（秒）
    }
)


@modules.import_package(package_name=setting.CRONTAB_PACKAGE_NAME, scan_prior=True)
def creat_app():
    """调度器主启动函数"""
    logging.info("===== 开始启动定时任务调度器 =====")
    global blocking
    # 打印已注册的任务列表，便于验证
    jobs = blocking.get_jobs()
    if jobs:
        logging.info(f"成功加载 {len(jobs)} 个定时任务:")
        for job in jobs:
            logging.info(f"  - 任务ID: {job.id} | 触发器: {job.trigger}")
    else:
        logging.warning("未发现任何定时任务，请检查任务模块是否正确配置")

    logging.info("调度器启动成功，开始运行任务 (按 Ctrl+C 停止)")
    return blocking
