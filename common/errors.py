from sanic.exceptions import SanicException


class UnauthorisedError(SanicException):
    message = "Unauthorised access...!"
    status_code = 401
    quiet = False


class DBAccessError(SanicException):
    message = "DB access error...!"
    status_code = 500
    quiet = False


class BadRequestError(SanicException):
    message = "Bad request...! :( 🔍"
    status_code = 400
    quiet = False

class NoFlowError(SanicException):
    message = "That flow was not found...! :( 🔍"
    status_code = 404
    quiet = True