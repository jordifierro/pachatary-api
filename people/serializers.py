def serialize_auth_token(auth_token):
    return {
               'access_token': auth_token.access_token,
               'refresh_token': auth_token.refresh_token
           }
