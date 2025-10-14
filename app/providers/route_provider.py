import logging

from routes.api import api_router


def boot(app):
    """
    初始化应用的路由配置。

    Args:
        app: FastAPI 应用实例
    """

    # ------------------------
    # 1. 注册 API 路由
    # ------------------------
    # 将 api_router 包含进主应用，并添加统一前缀 /api
    # 例如：api_router 中定义的 /users 路径，最终访问路径为 /api/users
    app.include_router(api_router, prefix="/api")

    # ------------------------
    # 2. 开发环境调试：打印路由信息
    # ------------------------
    # 当应用处于 debug 模式时，遍历所有注册的路由并打印
    # 方便开发者查看路由路径、名称和允许的 HTTP 方法
    if app.debug:
        for route in app.routes:
            # FastAPI 路由可能有多种类型，我们只关注 API 路由
            if hasattr(route, "methods") and hasattr(route, "endpoint"):
                methods = ", ".join(route.methods) if route.methods else "N/A"
                path = route.path
                handler_name = getattr(route.endpoint, "__name__", "N/A")
                logging.info("%-6s %-30s %-30s", methods, path, handler_name)
