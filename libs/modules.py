import importlib
import logging
import pkgutil
from typing import Tuple, List, Callable


class auto_import_modules:
    """
    装饰器：自动扫描并导入指定包下的模块，支持子包。
    使用方法：
        @scan_package("app.jobs", include_subpackages=True)
        def create_scheduler():
            ...
    """

    def __init__(self, package_name: str, include_subpackages: bool = False):
        self.package_name = package_name
        self.include_subpackages = include_subpackages

    def __call__(self, func: Callable):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            success_count, failed_modules = package_modules(
                self.package_name, self.include_subpackages
            )

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

            return result

        return wrapper


def package_modules(package_name: str, include_subpackages: bool = False) -> Tuple[int, List[str]]:
    """
    自动扫描并导入指定包下的所有模块

    :param package_name: 要扫描的包名（如"app.jobs"）
    :param include_subpackages: 是否包含子包，默认为False
    :return: 元组(成功导入的模块数, 导入失败的模块详情列表)
    """
    try:
        package = importlib.import_module(package_name)
        success_count = 0
        failed_modules: List[str] = []

        for loader, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
            module_path = f"{package_name}.{module_name}"
            try:
                # 导入模块或递归导入子包
                if is_pkg and include_subpackages:
                    sub_success, sub_failed = package_modules(module_path, include_subpackages)
                    success_count += sub_success
                    failed_modules.extend(sub_failed)
                else:
                    importlib.import_module(module_path)
                    success_count += 1
            except Exception as e:
                failed_modules.append(f"{module_path} (错误: {e.__class__.__name__}: {e})")

        return success_count, failed_modules

    except ImportError as e:
        return 0, [f"无法导入包: {package_name}，错误: {e}"]
    except AttributeError as e:
        return 0, [f"包结构错误: {package_name} 不是有效的包，错误: {e}"]
    except Exception as e:
        return 0, [f"模块处理过程发生意外错误: {e}"]
