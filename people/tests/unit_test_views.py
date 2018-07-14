from mock import Mock

from people.entities import AuthToken, Person
from people.views import PeopleView, PersonView, EmailConfirmationView, LoginEmailView, LoginView
from people.serializers import serialize_auth_token


class TestPeopleView:

    def test_post_returns_auth_token_serialized_and_201(self):
        TestPeopleView._ScenarioMaker() \
                .given_an_auth_token() \
                .given_an_interactor_that_returns_that_auth_token() \
                .given_a_client_secret_key() \
                .when_post_is_called_with_that_key() \
                .then_interactor_receives_that_key() \
                .then_response_status_is_201() \
                .then_response_body_is_auth_token_serialized()

    class _ScenarioMaker:

        def __init__(self):
            self.interactor_mock = Mock()
            self.interactor_mock.set_params.return_value = self.interactor_mock
            self.auth_token = None
            self.client_secret_key = None
            self.response = None

        def given_an_auth_token(self):
            self.auth_token = AuthToken(person_id='2', access_token='A', refresh_token='R')
            return self

        def given_a_client_secret_key(self):
            self.client_secret_key = 'scrt_ky'
            return self

        def given_an_interactor_that_returns_that_auth_token(self):
            self.interactor_mock.execute.return_value = self.auth_token
            return self

        def when_post_is_called_with_that_key(self):
            view = PeopleView(create_guest_person_and_return_auth_token_interactor=self.interactor_mock)
            self.body, self.status = view.post(client_secret_key=self.client_secret_key)
            return self

        def then_interactor_receives_that_key(self):
            self.interactor_mock.set_params.assert_called_once_with(client_secret_key=self.client_secret_key)
            return self

        def then_response_status_is_201(self):
            assert self.status == 201
            return self

        def then_response_body_is_auth_token_serialized(self):
            assert self.body == serialize_auth_token(self.auth_token)
            return self


class TestPersonView:

    def test_patch_returns_person_serialized_and_200(self):
        TestPersonView._ScenarioMaker() \
                .given_a_username() \
                .given_an_email() \
                .given_a_logged_person_id() \
                .given_a_person() \
                .given_an_interactor_that_returns_true() \
                .when_patch_is_called_with_that_params() \
                .then_interactor_receives_that_params() \
                .then_response_status_is_204() \
                .then_response_body_should_be_none()

    class _ScenarioMaker:

        def __init__(self):
            self.interactor_mock = Mock()
            self.interactor_mock.set_params.return_value = self.interactor_mock
            self.username = None
            self.email = None
            self.logged_person_id = None
            self.person = None
            self.response = None

        def given_a_username(self):
            self.username = 'usr.nm'
            return self

        def given_an_email(self):
            self.email = 'usr@em.c'
            return self

        def given_a_logged_person_id(self):
            self.logged_person_id = '4'
            return self

        def given_a_person(self):
            self.person = Person(id='8', email='b', is_email_confirmed=False)
            return self

        def given_an_interactor_that_returns_true(self):
            self.interactor_mock.execute.return_value = True
            return self

        def when_patch_is_called_with_that_params(self):
            view = PersonView(register_username_and_email_interactor=self.interactor_mock)
            self.body, self.status = view.patch(logged_person_id=self.logged_person_id,
                                                username=self.username, email=self.email)
            return self

        def then_interactor_receives_that_params(self):
            self.interactor_mock.set_params.assert_called_once_with(logged_person_id=self.logged_person_id,
                                                                    username=self.username, email=self.email)
            return self

        def then_response_status_is_204(self):
            assert self.status == 204
            return self

        def then_response_body_should_be_none(self):
            assert self.body is None
            return self


class TestEmailConfirmationView:

    def test_post_returns_204(self):
        TestEmailConfirmationView._ScenarioMaker() \
                .given_a_logged_person_id() \
                .given_a_confirmation_token() \
                .given_an_interactor_that_returns_true() \
                .when_post_is_called_with_that_params() \
                .then_interactor_receives_that_params() \
                .then_response_status_is_204() \
                .then_response_body_should_be_empty()

    class _ScenarioMaker:

        def __init__(self):
            self.interactor_mock = Mock()
            self.interactor_mock.set_params.return_value = self.interactor_mock
            self.logged_person_id = None
            self.confirmation_token = None
            self.response = None

        def given_a_logged_person_id(self):
            self.logged_person_id = '4'
            return self

        def given_a_confirmation_token(self):
            self.confirmation_token = 'ABC'
            return self

        def given_an_interactor_that_returns_true(self):
            self.interactor_mock.execute.return_value = True
            return self

        def when_post_is_called_with_that_params(self):
            view = EmailConfirmationView(confirm_email_interactor=self.interactor_mock)
            self.body, self.status = view.post(logged_person_id=self.logged_person_id,
                                               confirmation_token=self.confirmation_token)
            return self

        def then_interactor_receives_that_params(self):
            self.interactor_mock.set_params.assert_called_once_with(logged_person_id=self.logged_person_id,
                                                                    confirmation_token=self.confirmation_token)
            return self

        def then_response_status_is_204(self):
            assert self.status == 204
            return self

        def then_response_body_should_be_empty(self):
            assert self.body is None
            return self


class TestLoginEmailView:

    def test_post_returns_204(self):
        TestLoginEmailView.ScenarioMaker() \
                .given_an_email() \
                .when_post_is_called_with_that_params() \
                .then_interactor_receives_that_params() \
                .then_response_status_is_204()

    class ScenarioMaker:

        def __init__(self):
            self.interactor_mock = Mock()
            self.interactor_mock.set_params.return_value = self.interactor_mock
            self.email = None
            self.response = None

        def given_an_email(self):
            self.email = 'e'
            return self

        def when_post_is_called_with_that_params(self):
            view = LoginEmailView(login_email_interactor=self.interactor_mock)
            self.body, self.status = view.post(email=self.email)
            return self

        def then_interactor_receives_that_params(self):
            self.interactor_mock.set_params.assert_called_once_with(email=self.email)
            return self

        def then_response_status_is_204(self):
            assert self.status == 204
            assert self.body is None
            return self


class TestLoginView:

    def test_post_returns_200_and_person_and_auth_token(self):
        TestLoginView.ScenarioMaker() \
                .given_a_login_token() \
                .given_an_auth_token() \
                .given_an_interactor_that_returns_auth_token() \
                .when_post_is_called_with_that_params() \
                .then_interactor_receives_that_params() \
                .then_response_status_is_200() \
                .then_response_content_is_auth_token_serialized()

    class ScenarioMaker:

        def given_a_login_token(self):
            self.login_token = 'e'
            return self

        def given_an_auth_token(self):
            self.auth_token = AuthToken('9', 'a', 'r')
            return self

        def given_an_interactor_that_returns_auth_token(self):
            self.interactor_mock = Mock()
            self.interactor_mock.set_params.return_value = self.interactor_mock
            self.interactor_mock.execute.return_value = self.auth_token
            return self

        def when_post_is_called_with_that_params(self):
            view = LoginView(login_interactor=self.interactor_mock)
            self.body, self.status = view.post(token=self.login_token)
            return self

        def then_interactor_receives_that_params(self):
            self.interactor_mock.set_params.assert_called_once_with(login_token=self.login_token)
            return self

        def then_response_status_is_200(self):
            assert self.status == 200
            return self

        def then_response_content_is_auth_token_serialized(self):
            assert self.body == serialize_auth_token(self.auth_token)
            return self
