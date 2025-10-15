# FastAPI Skeleton

一个基于FastAPI的现代化、可扩展的后端服务框架，为开发者提供坚实的基础，加速高质量API服务的开发。

## 📋 项目特性

- **模块化架构**：采用清晰的模块化设计，便于代码组织和维护
- **认证系统**：集成JWT认证，提供安全可靠的身份验证机制
- **数据模型**：基于SQLAlchemy ORM，支持软删除等高级功能
- **异常处理**：统一的异常处理机制，确保API响应一致性
- **日志系统**：结构化日志配置，支持按天滚动和自动清理
- **路由系统**：基于FastAPI的强大路由功能，支持API分组和标签
- **提供器模式**：灵活的组件注册机制，便于功能扩展
- **应用工厂**：使用工厂函数创建应用实例，支持不同环境配置
- **定时任务系统**：基于APScheduler，支持自动扫描和注册任务

## 🚀 快速开始

### 环境要求

- Python 3.8+ 
- pip
- SQLite (默认数据库)

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动服务

```bash
python main.py
```

服务将在 http://localhost:8000 启动。

访问 http://localhost:8000/docs 查看自动生成的API文档。

## 🛠️ 核心模块

### 应用引导

应用使用工厂函数模式创建FastAPI实例，通过提供器机制注册各种组件：

```python
# bootstrap/application.py
def create_app() -> FastAPI:
    app = FastAPI(debug=True, default_response_class=ORJSONResponse)
    register(app, handle_exception)  # 注册异常处理
    register(app, logging_provider)  # 注册日志
    boot(app, route_provider)        # 启动路由
    return app
```

### 配置管理

配置集中管理在`config/setting.py`文件中：

```python
# 数据库配置
DATABASE_URL = "sqlite:///" + os.path.join(BASE_DIR, "storage", "db.sqlite3")

# JWT配置
SECRET_KEY = "your-secret-key"  # 请在生产环境中使用安全的密钥

# 日志配置
LOG_LEVEL = "INFO"
LOG_PATH = os.path.join(BASE_DIR, "storage", "logs", "fastapi-{time:YYYY-MM-DD}.log")
LOG_RETENTION = "14 days"
```

### 创建新路由

1. 在`app/http/`目录下创建新的模块目录
2. 在模块目录中创建`route.py`文件，定义路由和处理函数
3. 在`routes/api.py`中包含新路由模块

```python
# 在 routes/api.py 中添加
from app.http.new_module.route import router as newModuleRoute
api_router.include_router(newModuleRoute, tags=["new_module"])
```

### 添加新模型

1. 在`app/models/`目录下创建新的模型文件
2. 继承基础模型类并定义字段

```python
# 示例：创建产品模型
from sqlalchemy import Column, Integer, String
from base.model import BaseModel

class Product(BaseModel):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    price = Column(Integer, nullable=False)
    # 其他字段...
```

### 创建定时任务

1. 在`app/crontab/`目录下创建新的Python文件（如`your_task.py`）
2. 导入全局调度器并使用装饰器定义任务
3. 调度器会自动扫描并注册该任务

```python
# 示例：每分钟执行一次的任务
import datetime
from bootstrap.scheduler import scheduler

@scheduler.scheduled_job('cron', minute='*', id='minute_task')
def minute_task():
    print(f"[Task] 当前时间: {datetime.datetime.now()}")

# 示例：每天凌晨1点执行的任务
@scheduler.scheduled_job('cron', hour=1, minute=0, id='daily_task')
def daily_task():
    print(f"[Daily Task] 执行日期: {datetime.date.today()}")
```

### 启动定时任务

使用以下命令启动定时任务调度器：

```bash
python scheduler.py
```

调度器启动后会一直运行，并按照任务定义的时间规则执行相应任务。使用Ctrl+C可以优雅地关闭调度器。
### 环境配置

可以根据不同环境（开发、测试、生产）创建不同的配置文件，并在启动时指定：

```bash
# 生产环境启动示例
APP_ENV=production python main.py
```

## 🔐 安全注意事项

- 生产环境中请修改`config/setting.py`中的`SECRET_KEY`为随机生成的高强度密钥
- 不要将敏感配置信息硬编码在代码中，建议使用环境变量
- 定期轮换密码和密钥
- 确保日志文件不包含敏感信息

## 🤝 贡献指南

1. Fork 项目仓库
2. 创建功能分支
3. 提交代码更改
4. 推送到远程分支
5. 创建 Pull Request

## 📧 联系我们

如有问题或建议，请随时联系项目维护者。
