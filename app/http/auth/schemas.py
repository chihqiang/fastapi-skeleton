from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """
    登录请求数据模型

    用于验证客户端提交的登录表单数据，确保包含必要的用户名和密码字段，
    并提供示例值辅助API文档生成（如Swagger）。
    """

    # 邮箱字段，必填项，无默认值，示例值为"admin@example.com"
    email: str = Field(..., example="admin@example.com")
    # 密码字段，必填项，无默认值，示例值为"123456"
    password: str = Field(..., example="123456")


class TokenResponse(BaseModel):
    """
    登录成功后的令牌响应模型

    用于规范登录成功时返回的令牌信息格式，包含令牌类型、过期时间和访问令牌。
    """

    # 令牌类型，固定为"bearer"（符合OAuth 2.0规范），无需客户端传入
    token_type: str = "bearer"
    # 令牌过期时间（单位：秒），表示access_token的有效时长
    expires_in: int
    # 访问令牌字符串，客户端后续请求需携带此令牌进行身份验证
    access_token: str


class SendCodeRequest(BaseModel):
    """发送验证码请求模型"""

    email: EmailStr = Field(
        ...,
        example="user@example.com",
        description="接收验证码的邮箱地址（需符合标准格式）",
    )


class VerifyCodeRequest(BaseModel):
    """验证验证码请求模型"""

    email: EmailStr = Field(
        ..., example="user@example.com", description="接收验证码的邮箱地址"
    )
    code: str = Field(..., example="123456", description="验证码")
