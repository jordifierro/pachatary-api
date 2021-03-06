from .exceptions import InvalidEntityException, EntityDoesNotExistException, ConflictException, \
        PachataryException, NoLoggedException, NoPermissionException, BlockedContentException
from .serializers import serialize_exception

exception_status_code_mapper = {
        InvalidEntityException: 422,
        EntityDoesNotExistException: 404,
        ConflictException: 409,
        NoLoggedException: 401,
        NoPermissionException: 403,
        BlockedContentException: 403,
    }


def serialize_exceptions(func):
    def func_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PachataryException as e:
            body = serialize_exception(e)
            status = exception_status_code_mapper[type(e)]
        return body, status
    return func_wrapper
