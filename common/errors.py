from sanic.exceptions import SanicException


class UnauthorisedError(SanicException):
    message = "Unauthorised access...!"
    status_code = 401
    quiet = False


class DBAccessError(SanicException):
    message = "DB access error...!"
    status_code = 500
    quiet = False
