import time

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.exceptions.exception import BusinessException
from app.http.auth import service
from app.http.auth.schemas import (LoginRequest, SendCodeRequest,
                                   VerifyCodeRequest)
from app.support import depts
from app.support.fast import JSONSuccess
from libs import cache, strings

router = APIRouter(prefix="/auth")


def send_code_logic(email: str, code: str) -> None:
    """发送验证码邮件（实际场景替换为真实邮件服务）"""
    # 模拟发送延迟（真实场景为邮件API调用耗时）
    time.sleep(1)
    print(f"【验证码邮件】向 {email} 发送成功，验证码：{code}（5分钟内有效）")


@router.post("/send/code")
async def sendCode(request: SendCodeRequest, background_tasks: BackgroundTasks):
    code = strings.random_string()
    cache.set(request.email, code, 300)
    background_tasks.add_task(func=send_code_logic, email=request.email, code=code)
    return JSONSuccess(
        data={"email": request.email, "expire_seconds": 300},
        message="验证码已发送，请注意查收",
    )


@router.post("/verify/code")
async def verifyCode(request: VerifyCodeRequest):
    try:
        key = request.email
        stored_code = cache.get(key)
        if not stored_code:
            raise BusinessException(message="验证码不存在或已过期，请重新获取")
        if request.code != stored_code:
            raise BusinessException(message="验证码不正确，请重新输入")
        cache.delete(key)
        return JSONSuccess(
            data={"email": request.email, "verified": True}, message="验证码验证通过"
        )
    except Exception as e:
        raise BusinessException(
            message=f"验证码验证失败：{str(e)}",
        )


@router.post("/login")
async def login(request: LoginRequest, db: Session = Depends(depts.get_db)):
    response = service.loginToken(request.username, request.password, db)
    return JSONSuccess(data=response)
