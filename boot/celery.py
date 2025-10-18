import logging

from celery import Celery

from config import setting
from libs import modules

app = Celery(
    'queue',
    broker=f"sqla+{setting.DATABASE_URL}"
)

# 高级配置（可选）
app.conf.update(
    result_expires=3600,  # 结果过期时间（秒）
)


@modules.loader(package_name=setting.JOB_PACKAGE_NAME, scan_prior=True)
def create_app() -> Celery:
    global app
    registered_tasks = list(app.tasks.keys())

    custom_tasks = [task for task in registered_tasks if not task.startswith('celery.')]
    if custom_tasks:
        logging.info(f"成功加载 {len(custom_tasks)} 个自定义任务:")
        for task in custom_tasks[:5]:  # 只显示前5个，避免日志过长
            logging.info(f"  - {task}")
        if len(custom_tasks) > 5:
            logging.info(f"  - 以及 {len(custom_tasks) - 5} 个更多任务...")
    else:
        logging.warning("未发现任何自定义任务，请检查任务模块是否正确配置")
    return app
