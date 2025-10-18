from fastapi.exceptions import RequestValidationError
from fastapi import status, HTTPException, Request
from app.exceptions.exception import AuthenticationError, AuthorizationError
from app.support.fast import JSONCodeError


def register(app):
    """
    注册应用的全局异常处理器。
    """

    @app.exception_handler(AuthenticationError)
    async def authentication_exception_handler(request: Request, e: AuthenticationError):
        """
        处理身份验证失败的异常 (AuthenticationError)
        返回 HTTP 401 未授权响应
        """
        # 转成 dict 再返回
        return JSONCodeError(code=status.HTTP_401_UNAUTHORIZED, message=e.message)

    @app.exception_handler(AuthorizationError)
    async def authorization_exception_handler(request: Request, e: AuthorizationError):
        """
        处理权限不足的异常 (AuthorizationError)
        返回 HTTP 403 禁止访问响应
        """
        return JSONCodeError(message=e.message, code=status.HTTP_403_FORBIDDEN)

    @app.exception_handler(HTTPException)
    async def custom_http_exception_handler(request: Request, e: HTTPException):
        """
        处理 StarletteHTTPException 异常
        """
        return JSONCodeError(message=e.detail, code=e.status_code)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, e: RequestValidationError):
        """
        处理请求验证异常 (RequestValidationError)
        """
        errors = e.errors()
        if errors:
            full_message = ", ".join(err.get('msg', "参数校验错误") for err in errors)
        else:
            full_message = "参数校验失败"
        return JSONCodeError(message=full_message, code=status.HTTP_422_UNPROCESSABLE_ENTITY)
