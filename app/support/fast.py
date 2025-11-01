from datetime import datetime
from typing import Any, Optional

from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel


def _convert_pydantic_to_dict(data: Any) -> Any:
    """
    递归转换数据为可 JSON 序列化格式
    支持：Pydantic 模型、datetime、列表、字典、None 等
    """
    # 处理 None（避免空值递归报错）
    if data is None:
        return None
    # 处理 Pydantic 模型（优先转换为字典）
    if isinstance(data, BaseModel):
        return _convert_pydantic_to_dict(data.dict())
    # 处理 datetime 类型（核心序列化逻辑）
    if isinstance(data, datetime):
        return data.isoformat()
    # 处理列表（递归转换每个元素）
    if isinstance(data, list):
        return [_convert_pydantic_to_dict(item) for item in data]
    # 处理字典（递归转换每个值）
    if isinstance(data, dict):
        return {k: _convert_pydantic_to_dict(v) for k, v in data.items()}
    return data


def createJSONResponse(
    code: int, message: str, data: Optional[Any] = None, http_code: int = 200
) -> Response:
    response_data = {
        "code": code,
        "message": message,
        "data": _convert_pydantic_to_dict(data),
    }
    return JSONResponse(content=response_data, status_code=http_code)


def JSONSuccess(data: Optional[Any] = None, message: str = "success"):
    return createJSONResponse(code=200, data=data, message=message)


def JSONError(message: str = "Error", code: int = 500, http_code: int = 200):
    return createJSONResponse(code=code, message=message, http_code=http_code)


def JSONCodeError(code: int = 500, message: str = "Error"):
    return JSONError(code=code, message=message, http_code=code)
