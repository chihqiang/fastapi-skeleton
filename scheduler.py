import logging
from bootstrap.scheduler import create_scheduler

# 创建调度器实例，注册所有任务
scheduler = create_scheduler()

if __name__ == "__main__":
    try:
        # 启动调度器（阻塞模式）
        # 调度器启动后会一直运行，按任务定义的触发器执行任务
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        # 捕获键盘中断 (Ctrl+C) 或系统退出事件
        logging.info("Scheduler will shutdown...")  # 打印日志提示调度器即将关闭
        scheduler.shutdown()  # 优雅关闭调度器，停止所有任务
