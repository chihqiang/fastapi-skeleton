import importlib
import pkgutil
from typing import Tuple, List


def package_modules(package_name: str, include_subpackages: bool = False) -> Tuple[int, List[str]]:
    """
    自动扫描并导入指定包下的所有模块

    :param package_name: 要扫描的包名（如"app.jobs"）
    :param include_subpackages: 是否包含子包，默认为False
    :return: 元组(成功导入的模块数, 导入失败的模块详情列表)
    """
    try:
        # 动态导入指定包
        package = importlib.import_module(package_name)
        success_count = 0
        failed_modules = []
        # 遍历包下所有模块
        for loader, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
            # 根据参数决定是否处理子包
            if include_subpackages or not is_pkg:
                module_path = f"{package_name}.{module_name}"
                try:
                    # 如果是子包且需要处理，递归扫描子包
                    if is_pkg and include_subpackages:
                        sub_success, sub_failed = package_modules(module_path, include_subpackages)
                        success_count += sub_success
                        failed_modules.extend(sub_failed)
                    else:
                        # 导入模块
                        importlib.import_module(module_path)
                        success_count += 1
                except Exception as e:
                    error_detail = f"{module_path} (错误: {str(e)})"
                    failed_modules.append(error_detail)

        return success_count, failed_modules

    except ImportError as e:
        return 0, [f"无法导入包: {package_name}，错误: {str(e)}"]
    except AttributeError as e:
        return 0, [f"包结构错误: {package_name} 不是有效的包，错误: {str(e)}"]
    except Exception as e:
        return 0, [f"模块处理过程发生意外错误: {str(e)}"]
