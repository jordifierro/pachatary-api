class AuthTokenSerializer:

    @staticmethod
    def serialize(auth_token):
        return {
                   'access_token': auth_token.access_token,
                   'refresh_token': auth_token.refresh_token
               }


class PersonSerializer:

    @staticmethod
    def serialize(person):
        return {
                   'is_registered': person.is_registered,
                   'username': person.username,
                   'email': person.email,
                   'is_email_confirmed': person.is_email_confirmed,
               }


class PersonAuthTokenSerializer:

    @staticmethod
    def serialize(person, auth_token):
        return {
                   'person': PersonSerializer.serialize(person),
                   'auth_token': AuthTokenSerializer.serialize(auth_token)
               }
