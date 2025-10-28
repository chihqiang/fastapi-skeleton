from fastapi.encoders import jsonable_encoder
from pydantic.generics import GenericModel
from typing import Generic, TypeVar, Optional

from fastapi.responses import JSONResponse

T = TypeVar("T")


class BaseResponse(GenericModel, Generic[T]):
    """
    通用API响应模型，所有接口响应均遵循此格式
    继承GenericModel和Generic[T]以支持泛型数据类型
    """
    code: int = 200
    """业务状态码：200表示成功，其他值表示错误（可自定义错误码）"""
    message: str = "OK"
    """响应描述信息：成功/错误的文字说明"""
    data: Optional[T] = None
    """响应数据：成功时返回具体业务数据，错误时为None"""


def JSONSuccess(data: Optional[T] = None, message: str = "success"):
    """
    生成成功的JSONResponse响应
    直接返回可被FastAPI处理的HTTP响应对象，包含序列化后的成功数据

    :param data: 成功时需要返回的业务数据，可选（默认为None）
    :param message: 成功提示信息，可选（默认为"success"）
    :return: FastAPI的JSONResponse对象，HTTP状态码固定为200
    """
    # 先创建BaseResponse模型实例
    response = BaseResponse[T](code=200, message=message, data=data)
    # 转换为JSON响应：使用jsonable_encoder处理序列化，设置HTTP状态码为200
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder(response)
    )


def JSONError(message: str = "Error", code: int = 500, status_code: int = 200):
    """
    生成错误的JSONResponse响应（HTTP状态码固定为200）
    适用于前端统一处理响应格式的场景（通过业务code判断错误类型）

    :param message: 错误提示信息，可选（默认为"Error"）
    :param code: 业务错误码，可选（默认为500）
    :return: FastAPI的JSONResponse对象，HTTP状态码固定为200
    """
    # 先创建错误响应的BaseResponse模型实例
    response = BaseResponse[None](code=code, message=message, data=None)
    # 转换为JSON响应：HTTP状态码固定为200，业务错误通过code字段体现
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(response)
    )


def JSONCodeError(code: int = 500, message: str = "Error"):
    return JSONError(message=message, code=code, status_code=code)
