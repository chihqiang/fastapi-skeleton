from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.exceptions.exception import AuthenticationError, AuthorizationError


def register(app):
    """
    注册应用的全局异常处理器。

    Args:
        app: FastAPI 实例
    """

    @app.exception_handler(AuthenticationError)
    async def authentication_exception_handler(request: Request, e: AuthenticationError):
        """
        处理身份验证失败的异常 (AuthenticationError)
        返回 HTTP 401 未授权响应
        """
        return JSONResponse(status_code=401, content={"code": 401, "message": e.message, "data": None})

    @app.exception_handler(AuthorizationError)
    async def authorization_exception_handler(request: Request, e: AuthorizationError):
        """
        处理权限不足的异常 (AuthorizationError)
        返回 HTTP 403 禁止访问响应
        """
        return JSONResponse(status_code=403, content={"code": 403, "message": e.message, "data": None})

    @app.exception_handler(HTTPException)
    async def custom_http_exception_handler(request: Request, exc):
        """
        处理 StarletteHTTPException 异常
        可以直接调用 FastAPI 默认 http_exception_handler
        """
        # return await http_exception_handler(request, exc)
        return JSONResponse(status_code=200, content={"code": exc.status_code, "message": exc.detail, "data": None})

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc):
        """
        处理请求验证异常 (RequestValidationError)
        例如请求 body/params 格式不符合 Pydantic 模型
        """
        errors = exc.errors()
        if len(errors) > 0:
            full_message = ", ".join(err.get('msg', "参数校验错误") for err in errors)
        else:
            full_message = "参数校验失败"
        # return await request_validation_exception_handler(request, exc)
        return JSONResponse(status_code=200, content={"code": 422, "message": full_message, "data": None})
