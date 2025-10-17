import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from config import setting
from libs import modules

# 全局调度器实例，所有任务装饰器会使用它注册任务
blocking = BlockingScheduler(
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
def start():
    """调度器主启动函数"""
    logging.info("===== 开始启动定时任务调度器 =====")
    try:
        # 打印已注册的任务列表，便于验证
        jobs = blocking.get_jobs()
        if jobs:
            logging.info(f"成功加载 {len(jobs)} 个定时任务:")
            for job in jobs:
                logging.info(f"  - 任务ID: {job.id} | 触发器: {job.trigger}")
        else:
            logging.warning("未发现任何定时任务，请检查任务模块是否正确配置")

        logging.info("调度器启动成功，开始运行任务 (按 Ctrl+C 停止)")
        # 启动调度器（阻塞模式）
        blocking.start()

    except SystemExit:
        # 正常关闭流程
        logging.info("调度器正在关闭...")
        if 'scheduler' in locals():
            blocking.shutdown(wait=True)  # 等待当前任务完成后再关闭
            logging.info("调度器已安全关闭")
        logging.info("===== 调度器运行结束 =====")

    except Exception as e:
        # 捕获所有未预期的异常
        logging.error(f"调度器运行过程中发生致命错误: {str(e)}", exc_info=True)
        # 尝试紧急关闭
        if 'scheduler' in locals():
            blocking.shutdown(wait=False)  # 不等待，立即关闭
        logging.critical("调度器异常退出", exc_info=True)
