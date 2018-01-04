from .exceptions import InvalidEntityException, EntityDoesNotExistException, ConflictException, \
        PachataryException, NoLoggedException, NoPermissionException
from .serializers import PachataryExceptionSerializer

exception_status_code_mapper = {
        InvalidEntityException: 422,
        EntityDoesNotExistException: 404,
        ConflictException: 409,
        NoLoggedException: 401,
        NoPermissionException: 403,
        }


def serialize_exceptions(func):
    def func_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PachataryException as e:
            body = PachataryExceptionSerializer.serialize(e)
            status = exception_status_code_mapper[type(e)]
        return body, status
    return func_wrapper
