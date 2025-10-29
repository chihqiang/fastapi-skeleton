import random
import string
from typing import Literal


def random_digits(length: int = 6) -> str:
    """
    生成指定长度的纯数字随机字符串

    功能：从0-9的数字中随机选择字符，拼接成指定长度的字符串
    参数：
        length: 生成的数字字符串长度，必须为大于0的整数
    返回：
        str: 长度为length的纯数字字符串（如length=4时返回"1234"）
    异常：
        ValueError: 当length小于或等于0时抛出，提示"长度必须为正整数"
    """
    if length <= 0:
        raise ValueError("长度必须为正整数")
    # 从string.digits（包含"0123456789"）中随机选择字符，重复length次并拼接
    return "".join(random.choice(string.digits) for _ in range(length))


def random_letters(length: int = 6) -> str:
    """
    生成指定长度的纯字母随机字符串（包含大小写）

    功能：从大小写字母（a-z, A-Z）中随机选择字符，拼接成指定长度的字符串
    参数：
        length: 生成的字母字符串长度，必须为大于0的整数
    返回：
        str: 长度为length的纯字母字符串（如length=5时返回"aBcDe"）
    异常：
        ValueError: 当length小于或等于0时抛出，提示"长度必须为正整数"
    """
    if length <= 0:
        raise ValueError("长度必须为正整数")
    # 从string.ascii_letters（包含所有大小写字母）中随机选择字符，重复length次并拼接
    return "".join(random.choice(string.ascii_letters) for _ in range(length))


def random_chinese(length: int = 6) -> str:
    """
    生成指定长度的随机汉字字符串

    功能：从Unicode常用汉字范围（\u4e00-\u9fa5）中随机生成汉字，拼接成指定长度的字符串
    参数：
        length: 生成的汉字字符串长度，必须为大于0的整数
    返回：
        str: 长度为length的汉字字符串（如length=3时返回"你好呀"）
    异常：
        ValueError: 当length小于或等于0时抛出，提示"长度必须为正整数"
    说明：
        汉字范围基于Unicode编码，\u4e00-\u9fa5覆盖约2万个常用汉字，满足一般场景需求
    """
    if length <= 0:
        raise ValueError("长度必须为正整数")
    # 从Unicode常用汉字范围随机生成字符，重复length次并拼接
    return "".join(chr(random.randint(0x4E00, 0x9FA5)) for _ in range(length))


def random_string(
    length: int = 6, char_type: Literal["digit", "letter", "chinese"] = "digit"
) -> str:
    """
    生成指定长度和类型的随机字符串（汇总入口函数）

    功能：根据指定的字符类型，调用对应的生成函数，返回符合要求的随机字符串
    参数：
        length: 生成的字符串长度，必须为大于0的整数
        char_type: 字符类型（可选值）：
            - 'digit': 生成纯数字字符串（默认值）
            - 'letter': 生成纯字母字符串（包含大小写）
            - 'chinese': 生成随机汉字字符串
    返回：
        str: 符合长度和类型要求的随机字符串
    异常：
        ValueError:
            1. 当length小于或等于0时，由具体生成函数抛出
            2. 当char_type为不支持的类型时，提示"不支持的类型：xxx，可选类型：['digit', 'letter', 'chinese']"
    使用示例：
        generate_random_str(6, 'digit') → 生成6位数字（如"123456"）
        generate_random_str(4, 'letter') → 生成4位字母（如"AbCd"）
        generate_random_str(2, 'chinese') → 生成2个汉字（如"山水"）
    """
    # 类型与生成函数的映射关系，修复拼写错误（random_ters→random_letters，random_nese→random_chinese）
    type_mapping = {
        "digit": random_digits,
        "letter": random_letters,
        "chinese": random_chinese,
    }

    # 校验字符类型是否支持
    if char_type not in type_mapping:
        raise ValueError(
            f"不支持的类型：{char_type}，可选类型：{list(type_mapping.keys())}"
        )

    # 调用对应类型的生成函数并返回结果
    return type_mapping[char_type](length)
