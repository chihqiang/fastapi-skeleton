from typing import Any, Optional

from fastapi.responses import JSONResponse, Response


def createJSONResponse(
    code: int, message: str, data: Optional[Any] = None, http_code: int = 200
) -> Response:
    response_data = {"code": code, "message": message, "data": data}
    return JSONResponse(content=response_data, status_code=http_code)


def JSONSuccess(data: Optional[Any] = None, message: str = "success"):
    return createJSONResponse(code=200, data=data, message=message)


def JSONError(message: str = "Error", code: int = 500, http_code: int = 200):
    return createJSONResponse(code=code, message=message, http_code=200)


def JSONCodeError(code: int = 500, message: str = "Error"):
    return createJSONResponse(message=message, code=code, http_code=code)
