import uvicorn

from boot import logger
from boot.application import create_app

logger.setup()

# ------------------------
# 2. 创建 FastAPI 应用实例
# ------------------------
# create_app 是自定义的应用工厂函数，负责初始化应用
# 例如注册路由、异常处理、中间件等
app = create_app()


# ------------------------
# 3. 注册根路径路由
# ------------------------
# 定义一个简单的 GET 请求路由，用于测试应用是否启动成功
@app.get("/")
def index():
    return {"code": 200, "message": "welcome to fastapi skeleton"}


# ------------------------
# 4. 启动 ASGI 服务
# ------------------------
# 当该脚本直接执行时，使用 uvicorn 启动应用
# host="0.0.0.0" 表示接受任意 IP 访问
# port=8000 表示监听 8000 端口
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
