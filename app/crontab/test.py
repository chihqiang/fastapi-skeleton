import datetime

from boot.scheduler import scheduler


# 每分钟执行一次任务
@scheduler.scheduled_job('cron', minute='*', id='minute_job')
def minute_task():
    print(f"[Task] 当前时间: {datetime.datetime.now()}")