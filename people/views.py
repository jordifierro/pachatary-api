from pachatary.decorators import serialize_exceptions
from .serializers import AuthTokenSerializer, PersonSerializer, PersonAuthTokenSerializer


class PeopleView:

    def __init__(self, create_guest_person_and_return_auth_token_interactor=None):
        self.create_guest_person_and_return_auth_token_interactor = create_guest_person_and_return_auth_token_interactor

    @serialize_exceptions
    def post(self, client_secret_key, logged_person_id=None):
        auth_token = self.create_guest_person_and_return_auth_token_interactor \
                .set_params(client_secret_key=client_secret_key).execute()

        body = AuthTokenSerializer.serialize(auth_token)
        status = 201
        return body, status


class PersonView:

    def __init__(self, register_username_and_email_interactor=None):
        self.register_username_and_email_interactor = register_username_and_email_interactor

    @serialize_exceptions
    def patch(self, logged_person_id, username, email):
        person = self.register_username_and_email_interactor \
            .set_params(logged_person_id=logged_person_id, username=username, email=email).execute()

        body = PersonSerializer.serialize(person)
        status = 200
        return body, status


class EmailConfirmationView:

    def __init__(self, confirm_email_interactor=None):
        self.confirm_email_interactor = confirm_email_interactor

    @serialize_exceptions
    def post(self, logged_person_id, confirmation_token):
        updated_person = self.confirm_email_interactor.set_params(logged_person_id=logged_person_id,
                                                                  confirmation_token=confirmation_token).execute()

        body = PersonSerializer.serialize(updated_person)
        status = 200
        return body, status


class LoginEmailView:

    def __init__(self, login_email_interactor=None):
        self.login_email_interactor = login_email_interactor

    @serialize_exceptions
    def post(self, email, logged_person_id=None):
        self.login_email_interactor.set_params(email=email).execute()

        body = None
        status = 204
        return body, status


class LoginView:

    def __init__(self, login_interactor=None):
        self.login_interactor = login_interactor

    @serialize_exceptions
    def post(self, token, logged_person_id=None):
        person, auth_token = self.login_interactor.set_params(login_token=token).execute()

        body = PersonAuthTokenSerializer.serialize(person, auth_token)
        status = 200
        return body, status
