import datetime
from boot.scheduler import blocking


# ==========================================
# 定时任务示例 1：间隔触发（Interval）
# ==========================================
@blocking.scheduled_job('interval', seconds=10, id='interval_job')
def minute_task():
    """
    每隔 10 秒执行一次的任务
    - 'interval' 表示间隔触发器
    - seconds=10 表示每 10 秒执行一次
    - id='interval_job' 为这个任务分配唯一 ID，方便管理（修改、删除等）
    """
    print(f"[Task] 当前时间: {datetime.datetime.now()}")


# ==========================================
# 定时任务示例 2：Cron 表达式触发（Cron）
# ==========================================
@blocking.scheduled_job('cron', second=1, id="cron_job")
def trigger_worker_cron():
    """
    每分钟的第 1 秒执行一次的任务
    - 'cron' 表示使用 cron 触发器，可精确控制执行时间
    - second=1 表示在每分钟的第 1 秒触发
    - id="cron_job" 为任务分配唯一 ID
    """
    print(f"[Cron Task] 当前时间: {datetime.datetime.now()}")
