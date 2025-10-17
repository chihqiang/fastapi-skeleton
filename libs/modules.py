import importlib
import logging
import pkgutil
from typing import List, Callable


class loader:
    """
    装饰器：自动扫描并导入指定包下的模块（支持子包），并记录导入结果日志。

    特性：
    - 可递归扫描子包
    - 支持函数执行前或后导入
    - 避免重复导入同一包
    - 支持同步函数（如需异步支持可扩展）
    - 导入失败会记录到日志，而不会抛出异常
    """

    _scanned_packages = set()  # 类级缓存，用于避免重复导入同一包

    def __init__(self, package_name: str, include_subpackages: bool = False, scan_prior: bool = False):
        """
        初始化装饰器参数

        :param package_name: 要扫描的包名（如 "app.jobs"）
        :param include_subpackages: 是否递归扫描子包，默认为 False
        :param scan_prior: 扫描时机，True 表示在函数执行前扫描，False 表示在函数执行后扫描
        """
        self.package_name = package_name
        self.include_subpackages = include_subpackages
        self.scan_prior = scan_prior

    def __call__(self, func: Callable):
        """
        装饰器入口，将扫描逻辑插入被装饰函数执行前或后

        :param func: 被装饰的函数
        :return: 包装后的函数
        """
        def sync_wrapper(*args, **kwargs):
            # 前置扫描：函数执行前导入模块
            if self.scan_prior:
                self.loader_pkg_with_log()

            # 执行原函数逻辑
            result = func(*args, **kwargs)

            # 后置扫描：函数执行后导入模块
            if not self.scan_prior:
                self.loader_pkg_with_log()

            # 返回原函数返回值
            return result

        return sync_wrapper

    def loader_pkg_with_log(self):
        """
        扫描包并导入模块，同时记录日志。

        日志规则：
        - 成功导入全部模块：输出 info 日志
        - 部分模块导入失败：输出 warning 日志，列出失败模块及异常
        - 包为空：输出 info 日志
        """
        success_count, failed_modules = self.loader_pkg(self.package_name, self.include_subpackages)

        if not failed_modules:
            logging.info(f"✅ 成功导入 {self.package_name} 包下所有模块，共 {success_count} 个")
        else:
            logging.warning(
                f"⚠️ {self.package_name} 包模块导入完成 - "
                f"成功: {success_count} 个, 失败: {len(failed_modules)} 个"
            )
            for idx, error in enumerate(failed_modules, 1):
                logging.warning(f"  失败项 {idx}: {error}")

        if success_count == 0 and not failed_modules:
            logging.info(f"ℹ️ {self.package_name} 包下未发现任何可导入的模块")

    def loader_pkg(self, package_name: str, include_subpackages: bool = False) -> (int, List[str]):
        """
        扫描指定包及其模块并导入，返回扫描结果。

        :param package_name: 要扫描的包名
        :param include_subpackages: 是否递归扫描子包
        :return: (成功导入模块数, 导入失败模块列表)
        """
        # 避免重复导入同一包
        if package_name in self._scanned_packages:
            return 0, []

        try:
            # 导入根包
            package = importlib.import_module(package_name)
            success_count = 0
            failed_modules: List[str] = []

            # 遍历包下所有模块和子包
            for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
                module_path = f"{package_name}.{module_name}"
                try:
                    if is_pkg and include_subpackages:
                        # 递归扫描子包
                        sub_success, sub_failed = self.loader_pkg(module_path, include_subpackages)
                        success_count += sub_success
                        failed_modules.extend(sub_failed)
                    else:
                        # 导入普通模块
                        importlib.import_module(module_path)
                        success_count += 1
                except Exception as e:
                    # 捕获导入异常，记录失败模块
                    failed_modules.append(f"{module_path} (错误: {type(e).__name__}: {e})")

            # 标记包已扫描
            self._scanned_packages.add(package_name)
            return success_count, failed_modules

        except ImportError as e:
            return 0, [f"无法导入包: {package_name}，错误: {e}"]
        except AttributeError as e:
            return 0, [f"包结构错误: {package_name} 不是有效的包，错误: {e}"]
        except Exception as e:
            return 0, [f"模块处理过程发生意外错误: {e}"]
