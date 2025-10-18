# 导入FastAPI的JSON序列化工具，用于处理Pydantic模型到JSON的转换
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


def SuccessBaseResponse(data: Optional[T] = None, message: str = "success") -> BaseResponse[T]:
    """
    生成成功响应的BaseResponse模型实例
    用于需要返回Pydantic模型而非直接返回HTTP响应的场景

    :param data: 成功时需要返回的业务数据，可选（默认为None）
    :param message: 成功提示信息，可选（默认为"success"）
    :return: 包含成功信息的BaseResponse实例
    """
    return BaseResponse[T](code=200, message=message, data=data)


def JSONSuccess(data: Optional[T] = None, message: str = "success"):
    """
    生成成功的JSONResponse响应
    直接返回可被FastAPI处理的HTTP响应对象，包含序列化后的成功数据

    :param data: 成功时需要返回的业务数据，可选（默认为None）
    :param message: 成功提示信息，可选（默认为"success"）
    :return: FastAPI的JSONResponse对象，HTTP状态码固定为200
    """
    # 先创建BaseResponse模型实例
    response = SuccessBaseResponse(data=data, message=message)
    # 转换为JSON响应：使用jsonable_encoder处理序列化，设置HTTP状态码为200
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder(response)
    )


def ErrorBaseResponse(message: str = "Error", code: int = 500) -> BaseResponse[None]:
    """
    生成错误响应的BaseResponse模型实例
    用于需要返回Pydantic模型而非直接返回HTTP响应的场景

    :param message: 错误提示信息，可选（默认为"Error"）
    :param code: 业务错误码，可选（默认为500，代表服务器内部错误）
    :return: 包含错误信息的BaseResponse实例（data固定为None）
    """
    return BaseResponse[None](code=code, message=message, data=None)


def JSONError(message: str = "Error", code: int = 500):
    """
    生成错误的JSONResponse响应（HTTP状态码固定为200）
    适用于前端统一处理响应格式的场景（通过业务code判断错误类型）

    :param message: 错误提示信息，可选（默认为"Error"）
    :param code: 业务错误码，可选（默认为500）
    :return: FastAPI的JSONResponse对象，HTTP状态码固定为200
    """
    # 先创建错误响应的BaseResponse模型实例
    response = ErrorBaseResponse(message=message, code=code)
    # 转换为JSON响应：HTTP状态码固定为200，业务错误通过code字段体现
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder(response)
    )


def JSONCodeError(code: int = 500, message: str = "Error"):
    """
    生成错误的JSONResponse响应（HTTP状态码与业务code一致）
    符合HTTP规范的错误处理方式（如400对应参数错误，404对应资源不存在）

    :param code: 业务错误码（同时作为HTTP状态码），可选（默认为500）
    :param message: 错误提示信息，可选（默认为"Error"）
    :return: FastAPI的JSONResponse对象，HTTP状态码与code参数一致
    """
    # 先创建错误响应的BaseResponse模型实例
    response = ErrorBaseResponse(message=message, code=code)
    # 转换为JSON响应：HTTP状态码与业务错误码保持一致
    return JSONResponse(
        status_code=code,
        content=jsonable_encoder(response)
    )
