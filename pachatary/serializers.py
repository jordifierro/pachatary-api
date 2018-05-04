def serialize_picture(picture):
    if picture is None:
        return None

    return {
               'small_url': picture.small_url,
               'medium_url': picture.medium_url,
               'large_url': picture.large_url,
           }


def serialize_exception(exception):
    return {
               'error': {
                   'source': exception.source,
                   'code': exception.code,
                   'message': str(exception)
                }
           }
