class AppError(Exception):
    code: str = "APP_ERROR"
    status_code: int = 500

    def __init__(self, detail: str, code: str | None = None) -> None:
        super().__init__(detail)
        self.detail = detail
        if code is not None:
            self.code = code


class BadRequest(AppError):
    code = "BAD_REQUEST"
    status_code = 400


class Unauthorized(AppError):
    code = "UNAUTHORIZED"
    status_code = 401


class Forbidden(AppError):
    code = "FORBIDDEN"
    status_code = 403


class NotFound(AppError):
    code = "NOT_FOUND"
    status_code = 404


class Conflict(AppError):
    code = "CONFLICT"
    status_code = 409
