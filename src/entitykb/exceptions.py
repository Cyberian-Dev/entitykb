from fastapi import HTTPException
from starlette import status


class HTTP400(HTTPException):
    def __init__(self, detail: str, headers: dict = None):
        super(HTTP400, self).__init__(
            status.HTTP_400_BAD_REQUEST, detail, headers
        )


class HTTP401(HTTPException):
    def __init__(self, detail: str, headers: dict = None):
        super(HTTP401, self).__init__(
            status.HTTP_401_UNAUTHORIZED, detail, headers
        )


class HTTP404(HTTPException):
    def __init__(self, detail: str, headers: dict = None):
        super(HTTP404, self).__init__(
            status.HTTP_404_NOT_FOUND, detail, headers
        )


class HTTP409(HTTPException):
    def __init__(self, detail: str, headers: dict = None):
        super(HTTP409, self).__init__(
            status.HTTP_409_CONFLICT, detail, headers
        )


class HTTP500(HTTPException):
    def __init__(self, detail: str, headers: dict = None):
        super(HTTP500, self).__init__(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail, headers
        )


class DuplicateUsername(RuntimeError):
    pass


class InvalidUsername(RuntimeError):
    pass
