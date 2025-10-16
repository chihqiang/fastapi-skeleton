import importlib
import logging
import pkgutil
from typing import Tuple, List, Callable


class import_package:
    """
    装饰器：自动扫描并导入指定包下的模块（支持子包），并可控制扫描时机。

    核心功能：
    - 递归扫描指定包及其子包（可选），自动导入所有模块
    - 通过参数控制扫描行为在被装饰函数执行前/后触发
    - 记录导入结果日志（成功数量、失败详情）

    使用示例：
        @scan_package(
            package_name="app.crontab",  # 要扫描的包路径
            include_subpackages=True,    # 同时扫描子包
            scan_prior=True              # 先扫描再执行函数
        )
        def create_scheduler():
            # 函数逻辑（如创建调度器）
            ...
    """

    def __init__(
            self,
            package_name: str,
            include_subpackages: bool = False,
            scan_prior: bool = False
    ):
        """
        初始化装饰器参数

        :param package_name: 要扫描的包名（如"app.jobs"），必须是可导入的有效包路径
        :param include_subpackages: 是否递归扫描子包，默认为False（仅扫描当前包）
        :param scan_prior: 扫描时机控制，True=函数执行前扫描，False=函数执行后扫描，默认为False
        """
        self.package_name = package_name  # 目标包名
        self.include_subpackages = include_subpackages  # 是否包含子包
        self.scan_prior = scan_prior  # 扫描时机标记

    def __call__(self, func: Callable):
        """
        实现装饰器逻辑，包装被装饰的函数

        :param func: 被装饰的函数（如创建调度器的函数）
        :return: 包装后的函数，在执行前后插入扫描逻辑
        """

        def wrapper(*args, **kwargs):
            # 根据scan_prior决定扫描时机：True=函数执行前，False=函数执行后
            if self.scan_prior:
                self._scan_package_with_logger()  # 前置扫描

            # 执行被装饰的函数（核心业务逻辑）
            result = func(*args, **kwargs)

            # 后置扫描（仅当scan_prior为False时执行）
            if not self.scan_prior:
                self._scan_package_with_logger()  # 后置扫描

            return result  # 返回原函数执行结果

        return wrapper

    def _scan_package_with_logger(self):
        """
        执行模块扫描并输出格式化日志（封装扫描逻辑与日志输出）
        调用内部的_scan_package函数获取结果，并根据结果打印不同级别日志
        """
        # 调用扫描函数，获取成功数量和失败详情
        success_count, failed_modules = _import_package(
            self.package_name, self.include_subpackages
        )

        # 日志输出：根据扫描结果分情况提示
        if not failed_modules:
            # 无失败项时，打印成功日志
            logging.info(f"✅ 成功导入 {self.package_name} 包下所有模块，共 {success_count} 个")
        else:
            # 有失败项时，打印警告及失败详情
            logging.warning(
                f"⚠️ {self.package_name} 包模块导入完成 - "
                f"成功: {success_count} 个, 失败: {len(failed_modules)} 个"
            )
            # 逐条打印失败模块信息（便于排查问题）
            for idx, error in enumerate(failed_modules, 1):
                logging.warning(f"  失败项 {idx}: {error}")

        # 特殊情况：无成功也无失败（包为空）
        if success_count == 0 and not failed_modules:
            logging.info(f"ℹ️ {self.package_name} 包下未发现任何可导入的模块")


def _import_package(package_name: str, include_subpackages: bool = False) -> Tuple[int, List[str]]:
    """
    内部工具函数：实际执行模块扫描与导入的逻辑

    工作流程：
    1. 导入指定的根包
    2. 遍历包下所有模块/子包
    3. 对模块：直接导入；对子包：根据include_subpackages决定是否递归扫描
    4. 收集成功导入数量和失败详情

    :param package_name: 要扫描的包名（如"app.jobs"）
    :param include_subpackages: 是否递归扫描子包
    :return: 元组(成功导入的模块数, 导入失败的模块详情列表)
    """
    try:
        # 导入根包（若包不存在会触发ImportError）
        package = importlib.import_module(package_name)
        success_count = 0  # 成功导入的模块计数器
        failed_modules: List[str] = []  # 失败模块详情列表

        # 遍历包下所有模块/子包（通过pkgutil获取模块信息）
        for loader, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
            # 构建完整模块路径（根包.子模块名）
            module_path = f"{package_name}.{module_name}"
            try:
                # 处理子包：如果是包且需要递归，则递归调用扫描
                if is_pkg and include_subpackages:
                    # 递归扫描子包，累加结果
                    sub_success, sub_failed = _import_package(module_path, include_subpackages)
                    success_count += sub_success
                    failed_modules.extend(sub_failed)
                else:
                    # 处理普通模块：直接导入
                    importlib.import_module(module_path)
                    success_count += 1  # 导入成功则计数+1
            except Exception as e:
                # 捕获导入异常，记录失败详情（模块路径+错误信息）
                failed_modules.append(f"{module_path} (错误: {e.__class__.__name__}: {e})")

        return success_count, failed_modules

    # 处理包导入相关的异常
    except ImportError as e:
        return 0, [f"无法导入包: {package_name}，错误: {e}"]
    except AttributeError as e:
        # 通常是因为package_name不是有效包（无__path__属性）
        return 0, [f"包结构错误: {package_name} 不是有效的包，错误: {e}"]
    except Exception as e:
        # 捕获其他未预期的异常
        return 0, [f"模块处理过程发生意外错误: {e}"]
