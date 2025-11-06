from typing import Any, Callable, Iterable, Optional, Union


# -----------------------------
# 深度合并字典函数
# -----------------------------
def array_deep_merge(*dicts):
    """
    递归合并多个字典。
    如果相同键对应的值都是字典，会递归合并。
    否则，后面的值会覆盖前面的值。

    :param dicts: 任意数量的字典
    :return: 合并后的字典

    使用示例：
    >>> a = {'a': 1, 'b': {'x': 1}}
    >>> b = {'a': 2, 'b': {'y': 2}}
    >>> array_deep_merge(a, b)
    {'a': 2, 'b': {'x': 1, 'y': 2}}
    """

    def _merge(d1, d2):
        result = d1.copy()
        for k, v in d2.items():
            if k in result and isinstance(result[k], dict) and isinstance(v, dict):
                result[k] = _merge(result[k], v)
            else:
                result[k] = v
        return result

    merged = {}
    for d in dicts:
        merged = _merge(merged, d)
    return merged


def array_index(
    array: Iterable[dict],
    key: Optional[Union[str, Callable[[dict], Any]]] = None,
    group_key: Optional[str] = None,
):
    """
    将数组按指定键重新索引，支持分组和匿名函数生成键。

    :param array: 输入数组（多维数组或对象数组）
    :param key: 指定索引字段名或函数生成索引
    :param group_key: 可选，按指定字段分组
    :return: 索引或分组后的字典

    使用示例：

    # 示例 1: 按指定 key 索引（重复 key 会覆盖）
    >>> arr = [
    ...     {'id': '123', 'data': 'abc'},
    ...     {'id': '345', 'data': 'def'},
    ...     {'id': '345', 'data': 'hgi'},
    ... ]
    >>> array_index(arr, 'id')
    {'123': {'id': '123', 'data': 'abc'}, '345': {'id': '345', 'data': 'hgi'}}

    # 示例 2: 使用 lambda 函数生成 key
    >>> array_index(arr, lambda x: x['id'])
    {'123': {'id': '123', 'data': 'abc'}, '345': {'id': '345', 'data': 'hgi'}}

    # 示例 3: 按 group_key 分组（保留重复元素）
    >>> array_index(arr, None, 'id')
    {'123': [{'id': '123', 'data': 'abc'}],
     '345': [{'id': '345', 'data': 'def'}, {'id': '345', 'data': 'hgi'}]}

    # 示例 4: key 和 group_key 都指定
    >>> array_index(arr, 'data', 'id')
    {'123': [{'id': '123', 'data': 'abc'}],
     '345': [{'id': '345', 'data': 'def'}, {'id': '345', 'data': 'hgi'}]}
    """
    result = {}

    for element in array:
        # 计算索引 key
        if callable(key):
            k = key(element)
        elif isinstance(key, str):
            k = element.get(key)
        else:
            k = None

        # 分组处理
        if group_key:
            gk = element.get(group_key)
            if gk is None:
                result.setdefault(None, []).append(element)
            else:
                result.setdefault(gk, []).append(element)
        else:
            if k is not None:
                result[k] = element

    return result


def array_map(
    array: Iterable[dict],
    key: Union[str, Callable[[dict], Any]],
    value: Union[str, Callable[[dict], Any]],
    group: Optional[Union[str, Callable[[dict], Any]]] = None,
):
    """
    将数组映射为 key -> value，可选分组。

    :param array: 输入数组（列表字典）
    :param key: 指定 key 字段名或函数生成 key
    :param value: 指定 value 字段名或函数生成 value
    :param group: 可选，指定分组字段名或函数
    :return: 映射字典

    使用示例：

    # 示例 1: 不分组，直接映射 key -> value
    >>> arr = [
    ...     {'id': '123', 'name': 'aaa', 'class': 'x'},
    ...     {'id': '124', 'name': 'bbb', 'class': 'x'},
    ...     {'id': '345', 'name': 'ccc', 'class': 'y'},
    ... ]
    >>> array_map(arr, 'id', 'name')
    {'123': 'aaa', '124': 'bbb', '345': 'ccc'}

    # 示例 2: 按 group 分组
    >>> array_map(arr, 'id', 'name', 'class')
    {'x': {'123': 'aaa', '124': 'bbb'}, 'y': {'345': 'ccc'}}

    # 示例 3: 使用 lambda 函数生成 key/value/group
    >>> array_map(arr,
    ...           key=lambda x: x['id'],
    ...           value=lambda x: x['name'].upper(),
    ...           group=lambda x: x['class'])
    {'x': {'123': 'AAA', '124': 'BBB'}, 'y': {'345': 'CCC'}}
    """
    result = {}

    for element in array:
        # 计算 key
        k = key(element) if callable(key) else element.get(key)
        # 计算 value
        v = value(element) if callable(value) else element.get(value)

        # 分组处理
        if group:
            gk = group(element) if callable(group) else element.get(group)
            if gk not in result:
                result[gk] = {}
            result[gk][k] = v
        else:
            result[k] = v

    return result
