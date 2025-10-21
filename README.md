# FastAPI Skeleton

一个基于FastAPI的现代化、可扩展的后端服务框架，为开发者提供坚实的基础，加速高质量API服务的开发。

## 📋 项目特性

- **模块化架构**：采用清晰的模块化设计，便于代码组织和维护
- **认证系统**：集成JWT认证，提供安全可靠的身份验证机制
- **数据模型**：基于SQLAlchemy ORM，支持软删除等高级功能
- **异常处理**：统一的异常处理机制，确保API响应一致性和错误信息标准化
- **日志系统**：结构化日志配置，支持按天滚动和自动清理（14天保留期）
- **路由系统**：基于FastAPI的强大路由功能，支持API分组和标签，所有API路由统一以`/api`为前缀
- **提供器模式**：灵活的组件注册机制，便于功能扩展和模块化开发
- **应用工厂**：使用工厂函数创建应用实例，支持不同环境配置和生命周期管理
- **定时任务系统**：基于APScheduler，支持自动扫描和注册任务，具有任务合并、最大并发控制等高级特性
- **数据库支持**：默认使用SQLite，支持无缝切换到其他数据库（如MySQL、PostgreSQL等）
- **用户系统**：内置完整的用户模型，支持用户名、邮箱、手机号等多维度用户信息管理

## 🚀 快速开始

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

### 配置管理

配置集中管理在`config/setting.py`文件中，主要包括以下配置项：

```python
# 项目路径配置
BASE_DIR = Path(__file__).resolve().parent.parent

# 数据库配置（默认使用SQLite）
DATABASE_URL = "sqlite:///" + os.path.join(BASE_DIR, "storage", "db.sqlite3")

# 日志系统配置
LOG_LEVEL = "INFO"  # 日志级别
LOG_PATH = os.path.join(BASE_DIR, "storage", "logs", "fastapi-{time:YYYY-MM-DD}.log")  # 按天滚动的日志文件
LOG_RETENTION = "14 days"  # 日志保留时间

# JWT认证配置
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"  # 生产环境请修改为随机生成的密钥

# 定时任务配置
CRONTAB_PACKAGE_NAME = "app.crontab"  # 定时任务模块根包名
JOB_PACKAGE_NAME = "app.jobs"  # 业务任务模块根包名
```

### API路由系统

项目采用模块化的路由管理方式，所有API路由统一以`/api`为前缀。目前已实现的路由包括：

```python
# routes/api.py
from fastapi import APIRouter

from app.http.auth.route import router as authRoute
from app.http.user.route import router as userRoute

api_router = APIRouter()

api_router.include_router(authRoute, tags=["auth"])  # 认证相关路由
api_router.include_router(userRoute, tags=["user"])  # 用户相关路由
```

#### 创建新路由

1. 在`app/http/`目录下创建新的模块目录
2. 在模块目录中创建`route.py`文件，定义路由和处理函数
3. 在`routes/api.py`中包含新路由模块

```python
# 在 routes/api.py 中添加
from app.http.new_module.route import router as newModuleRoute
api_router.include_router(newModuleRoute, tags=["new_module"])  # 添加标签以便在API文档中分组显示
```

### 数据库模型系统

项目使用SQLAlchemy ORM进行数据库操作，提供了两个基础模型类：

1. `BaseModel`：基础模型，包含`created_at`和`updated_at`字段，自动记录创建和更新时间
2. `BaseModelWithSoftDelete`：扩展模型，在`BaseModel`基础上增加了软删除功能

#### 用户模型示例

```python
# app/models/user.py
class User(BaseModelWithSoftDelete):
    __tablename__ = "users"  # 数据库表名
    __table_args__ = {"comment": "用户表"}  # 表描述

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键，自增ID")
    username = Column(String(255), unique=True, nullable=False, comment="用户名，唯一，必填")
    password = Column(String(255), nullable=False, comment="密码哈希，bcrypt 加密")
    cellphone = Column(String(50), unique=True, nullable=False, comment="手机号，唯一，必填")
    email = Column(String(255), unique=True, nullable=False, comment="邮箱，唯一，必填")
    email_verified_at = Column(DateTime, nullable=True, comment="邮箱验证时间")
    state = Column(String(50), default='enabled', nullable=False, comment="用户状态，enabled 表示启用")
    nickname = Column(String(100), nullable=False, comment="昵称")
    gender = Column(String(50), default='unknown', nullable=False, comment="性别，unknown 表示未指定")
    avatar = Column(String(255), nullable=True, comment="头像 URL")
```

#### 添加新模型

1. 在`app/models/`目录下创建新的模型文件
2. 继承基础模型类并定义字段

```python
# 示例：创建产品模型
from sqlalchemy import Column, Integer, String
from base.model import BaseModel  # 或 BaseModelWithSoftDelete 如果需要软删除功能

class Product(BaseModel):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    price = Column(Integer, nullable=False)
    # 其他字段...
```

### 定时任务系统

项目使用APScheduler实现定时任务，具有任务自动扫描注册、任务合并、最大并发控制等特性。

#### 调度器配置

```python
# boot/scheduler.py
app = AsyncIOScheduler(
    jobstores={
        "default": SQLAlchemyJobStore(url=setting.DATABASE_URL),  # 使用数据库存储任务
    },
    timezone=getattr(setting, 'TIMEZONE', 'UTC'),  # 时区配置
    job_defaults={
        'coalesce': True,  # 合并错过的重复任务（避免任务堆积）
        'max_instances': 3,  # 同一任务最大并发实例数
        'misfire_grace_time': 30  # 任务误触发容忍时间（秒）
    }
)
```

#### 创建定时任务

1. 在`app/crontab/`目录下创建新的Python文件（如`your_task.py`）
2. 导入全局调度器并使用装饰器定义任务
3. 调度器会自动扫描并注册该任务

```python
# 示例：每分钟执行一次的任务
import datetime
from boot.scheduler import app


@app.scheduled_job('cron', minute='*', id='minute_task')
def minute_task():
    print(f"[Task] 当前时间: {datetime.datetime.now()}")


# 示例：每天凌晨1点执行的任务
@app.scheduled_job('cron', hour=1, minute=0, id='daily_task')
def daily_task():
    print(f"[Daily Task] 执行日期: {datetime.date.today()}")
```

### 异常处理机制

项目实现了统一的异常处理机制，支持处理多种类型的异常并返回标准化的错误响应：

- **AuthenticationError**：身份验证失败异常，返回HTTP 401状态码
- **AuthorizationError**：权限不足异常，返回HTTP 403状态码
- **HTTPException**：标准HTTP异常处理
- **RequestValidationError**：请求参数验证异常，返回HTTP 422状态码

所有异常都通过`JSONCodeError`返回标准化的错误格式，包含错误码和错误信息。

### 启动定时任务

使用以下命令启动定时任务调度器：

```bash
python scheduler.py
```

调度器启动后会自动扫描并注册`app.crontab`包下的所有任务，并输出已加载的任务列表。使用Ctrl+C可以优雅地关闭调度器。
### 环境配置与部署

#### 环境变量配置

可以根据不同环境（开发、测试、生产）设置环境变量来调整配置：

```bash
# 生产环境启动示例
APP_ENV=production python main.py
```

#### 数据库迁移

项目提供了数据库迁移工具，可以通过以下命令执行迁移：

```bash
python tools/migrate.py
```

#### 生产环境注意事项

1. 修改`config/setting.py`中的`SECRET_KEY`为随机生成的高强度密钥（推荐使用32位以上随机字符串）
2. 将`DEBUG`模式设置为`False`
3. 考虑使用更强大的数据库如PostgreSQL或MySQL
4. 配置适当的日志级别和存储路径
5. 设置合理的任务调度器参数

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
