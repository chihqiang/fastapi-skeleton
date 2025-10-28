from fastapi import status


class AuthenticationError(Exception):
    """
    自定义异常类，用于表示身份验证失败的情况。

    Attributes:
        message (str): 错误信息，默认为 "Unauthorized"。
    """

    def __init__(self, message: str = "Unauthorized"):
        self.message = message
        super().__init__(self.message)  # 确保 Exception 的基础行为正常


class AuthorizationError(Exception):
    """
    自定义异常类，用于表示权限不足或访问被禁止的情况。

    Attributes:
        message (str): 错误信息，默认为 "Forbidden"。
    """

    def __init__(self, message: str = "Forbidden"):
        self.message = message
        super().__init__(self.message)  # 确保 Exception 的基础行为正常


class BusinessException(Exception):
    """
    自定义业务异常类
    用于区分系统异常和业务逻辑异常
    """

    def __init__(self, message: str = "业务处理失败", code: int = 400, status_code: int = status.HTTP_200_OK):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)
