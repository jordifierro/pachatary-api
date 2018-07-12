def serialize_picture(picture):
    if picture is None:
        return None

    serialized = {}
    if picture.large_url is not None:
        serialized.update({'large_url': picture.large_url})
    if picture.medium_url is not None:
        serialized.update({'medium_url': picture.medium_url})
    if picture.small_url is not None:
        serialized.update({'small_url': picture.small_url})
    if picture.tiny_url is not None:
        serialized.update({'tiny_url': picture.tiny_url})
    return serialized


def serialize_exception(exception):
    return {
               'error': {
                   'source': exception.source,
                   'code': exception.code,
                   'message': str(exception)
                }
           }
