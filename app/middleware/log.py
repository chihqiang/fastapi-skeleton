import logging
import time

from fastapi import Request
from starlette.types import ASGIApp, Receive, Scope, Send


class Middleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        # 只处理HTTP请求
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # 构建请求对象
        request = Request(scope, receive)
        start_time = time.time()
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path
        # 用于捕获响应状态码
        status_code = 500  # 默认错误状态码

        async def send_wrapper(message: dict):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            # 处理请求
            await self.app(scope, receive, send_wrapper)
        except Exception as e:
            logging.error(
                f"{client_ip} - [{method}] {path} | 500 | {time.time() - start_time:.3f}s | 错误: {str(e)}"
            )
            raise
        else:
            # 计算响应时间（保留3位小数，与Gin一致）
            response_time = (time.time() - start_time) * 1000  # 转换为毫秒
            # [时间] [级别] 客户端IP - [方法] 路径 | 状态码 | 响应时间
            logging.info(
                f"{client_ip} - [{method}] {path} | {status_code} | {response_time:.3f}ms"
            )
