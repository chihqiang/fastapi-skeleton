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
