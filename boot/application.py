import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from app.providers import handle_exception, route_provider


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("应用生命周期启动 - 开始初始化资源")
    try:
        # TODO start process
        yield
        # TODO stop process
        logging.info("应用生命周期即将结束 - 开始清理资源")
    finally:
        logging.info("应用生命周期结束 - 所有资源已清理")


def create_app() -> FastAPI:
    app = FastAPI(debug=True, lifespan=lifespan, default_response_class=ORJSONResponse)
    register(app, handle_exception)  # 注册异常处理提供器
    boot(app, route_provider)  # 启动路由提供器
    return app


def register(app, provider):
    """
    注册提供器到应用中。

    参数:
    - app: FastAPI 应用实例
    - provider: 提供器对象，需要实现 register(app) 方法

    功能:
    调用 provider 的 register 方法，将其注册到 app 中，
    并记录日志表示注册完成。
    """
    provider.register(app)
    logging.info(provider.__name__ + " registered")  # 打印注册日志


def boot(app, provider):
    """
    启动提供器。

    参数:
    - app: FastAPI 应用实例
    - provider: 提供器对象，需要实现 boot(app) 方法

    功能:
    调用 provider 的 boot 方法来初始化或启动相关功能，
    并记录日志表示启动完成。
    """
    provider.boot(app)
    logging.info(provider.__name__ + " booted")  # 打印启动日志
