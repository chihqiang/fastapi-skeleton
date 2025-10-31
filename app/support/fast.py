from typing import Any, Optional

from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel


def _convert_pydantic_to_dict(data: Any) -> Any:
    """递归转换 Pydantic 模型为字典，支持嵌套结构"""
    if isinstance(data, BaseModel):
        # 处理单个 Pydantic 模型
        return data.dict()
    elif isinstance(data, list):
        # 处理列表，递归转换每个元素
        return [_convert_pydantic_to_dict(item) for item in data]
    elif isinstance(data, dict):
        # 处理字典，递归转换每个值
        return {k: _convert_pydantic_to_dict(v) for k, v in data.items()}
    else:
        # 非 Pydantic 类型直接返回
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
    return createJSONResponse(code=code, message=message, http_code=200)


def JSONCodeError(code: int = 500, message: str = "Error"):
    return createJSONResponse(message=message, code=code, http_code=code)
