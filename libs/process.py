import logging
import time
from multiprocessing import Process


class Manager:
    def __init__(self):
        """
        初始化进程管理器
        - self.processes: 存储已启动的 Process 对象
        - self.process_configs: 存储进程配置信息
        - self._original_functions: 存储原始函数引用，避免装饰器导致函数丢失
        """
        self.processes = []
        self.process_configs = []
        self._original_functions = {}

    def register(self, name, number=1, args=None, kwargs=None):
        """
        装饰器方式添加进程配置
        :param name: 进程名称
        :param number: 同一函数启动的进程数量
        :param args: 传递给函数的位置参数
        :param kwargs: 传递给函数的关键字参数
        """

        def decorator(target):
            func_key = target.__name__
            if func_key in self._original_functions:
                logging.warning(f"函数 {func_key} 已注册，跳过重复注册")
                return target

            self._original_functions[func_key] = target
            self.process_configs.append({
                "name": name,
                "func_key": func_key,
                "number": number,
                "args": args or (),
                "kwargs": kwargs or {}
            })
            logging.info(f"已通过装饰器添加进程：{name}（函数：{func_key}），数量：{number}")
            return target

        return decorator

    def start_all(self):
        """
        启动所有已配置的进程
        - 如果已有进程在运行，先调用 terminate_all() 清理
        - 遍历 process_configs，根据number参数创建多个进程
        - 将已启动的进程对象保存到 self.processes
        """
        if not self.process_configs:
            logging.warning("没有需要启动的进程配置")
            return False

        # 安全：先终止已有进程，再清空列表
        self.terminate_all()
        self.processes = []

        try:
            for config in self.process_configs:
                # 获取原始函数
                target_func = self._original_functions.get(config["func_key"])
                if not target_func:
                    logging.error(f"找不到进程[{config['name']}]的原始函数：{config['func_key']}")
                    continue

                # 根据number参数创建多个进程
                for i in range(config["number"]):
                    # 为每个进程生成唯一名称
                    process_name = f"{config['name']}-{i + 1}" if config["number"] > 1 else config["name"]

                    # 创建并启动进程
                    p = Process(name=process_name, target=target_func, args=config["args"], kwargs=config["kwargs"])
                    p.start()
                    self.processes.append(p)
                    logging.info(f"进程 [{process_name}] 启动成功，PID: {p.pid}")

            return len(self.processes) > 0
        except Exception as e:
            logging.error(f"启动进程时出错: {str(e)}", exc_info=True)
            self.terminate_all()
            return False

    def monitor_all(self, non_blocking=False, interval=1):
        """
        监控所有已启动的进程
        :param non_blocking: True 表示非阻塞轮询，False 表示阻塞 join
        :param interval: 非阻塞模式下轮询间隔（秒）
        """
        if not self.processes:
            logging.warning("没有可监控的进程")
            return

        try:
            if non_blocking:
                # 非阻塞模式：循环轮询进程状态
                while any(p.is_alive() for p in self.processes):
                    for p in self.processes:
                        # 只报告一次退出状态
                        if not p.is_alive() and getattr(p, "_reported", False) is False:
                            if p.exitcode == 0:
                                logging.info(f"进程 [{p.name}] 正常退出")
                            else:
                                logging.warning(f"进程 [{p.name}] 异常退出，退出码: {p.exitcode}")
                            p._reported = True
                    time.sleep(interval)
            else:
                # 阻塞模式：等待所有进程结束
                for p in self.processes:
                    p.join()
                    if p.exitcode == 0:
                        logging.info(f"进程 [{p.name}] 正常退出")
                    else:
                        logging.warning(f"进程 [{p.name}] 异常退出，退出码: {p.exitcode}")
        except KeyboardInterrupt:
            logging.info("收到中断信号，终止所有进程...")
            self.terminate_all()
        except Exception as e:
            logging.error(f"监控进程出错: {str(e)}", exc_info=True)
            self.terminate_all()

    def terminate_all(self, timeout=5):
        """
        终止所有仍在运行的进程
        :param timeout: join 等待进程结束的超时时间（秒）
        """
        for p in self.processes:
            if p.is_alive():
                logging.info(f"终止进程 [{p.name}]...")
                p.terminate()
                p.join(timeout=timeout)
                if p.is_alive():
                    logging.warning(f"进程 [{p.name}] 未能正常终止")

    def get_process_status(self):
        """
        获取所有已启动进程的状态信息
        :return: 列表，每个元素包含 name, pid, is_alive, exitcode
        """
        return [{
            "name": p.name,
            "pid": p.pid,
            "is_alive": p.is_alive(),
            "exitcode": p.exitcode
        } for p in self.processes]
