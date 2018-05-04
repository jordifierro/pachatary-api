def serialize_auth_token(auth_token):
    return {
               'access_token': auth_token.access_token,
               'refresh_token': auth_token.refresh_token
           }


def serialize_person(person):
    return {
               'is_registered': person.is_registered,
               'username': person.username,
               'email': person.email,
               'is_email_confirmed': person.is_email_confirmed,
           }


def serialize_person_auth_token(person, auth_token):
    return {
               'person': serialize_person(person),
               'auth_token': serialize_auth_token(auth_token)
           }
