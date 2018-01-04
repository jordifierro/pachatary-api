from mock import Mock

from abidria.exceptions import InvalidEntityException
from people.entities import Person, AuthToken
from people.interactors import CreateGuestPersonAndReturnAuthToken


class TestCreateGuestPersonAndReturnAuthToken(object):

    def test_creates_guest_person_and_returns_auth_token(self):
        TestCreateGuestPersonAndReturnAuthToken._ScenarioMaker() \
                .given_a_client_secret_key() \
                .given_a_client_secret_key_validator_that_accepts_that_key() \
                .given_a_person_repo_that_returns_a_person() \
                .given_an_auth_token_repo_that_returns_a_token() \
                .when_execute_interactor() \
                .then_response_should_be_that_token() \
                .then_client_secret_key_should_be_validated() \
                .then_person_repo_create_guest_person_should_be_called() \
                .then_create_auth_token_should_be_called_with_returned_person_id()

    def test_invalid_client_secret_key_returns_invalid_entity_exception_and_doesnt_create_person(self):
        TestCreateGuestPersonAndReturnAuthToken._ScenarioMaker() \
                .given_a_client_secret_key() \
                .given_a_client_secret_key_validator_that_doesnt_accept_that_key() \
                .given_a_person_repo_that_returns_a_person() \
                .given_an_auth_token_repo_that_returns_a_token() \
                .when_execute_interactor() \
                .then_should_raise_invalid_entity_exception() \
                .then_client_secret_key_should_be_validated() \
                .then_person_repo_create_guest_person_should_not_be_called() \
                .then_create_auth_token_should_not_be_called()

    class _ScenarioMaker(object):

        def __init__(self):
            self.person = None
            self.auth_token = None
            self.person_repo = None
            self.auth_token_repo = None
            self.response = None
            self.client_secret_key = None
            self.client_secret_key_validator = None

        def given_a_client_secret_key(self):
            self.client_secret_key = "scrt"
            return self

        def given_a_client_secret_key_validator_that_accepts_that_key(self):
            self.client_secret_key_validator = Mock()
            self.client_secret_key_validator.validate.return_value = True
            return self

        def given_a_client_secret_key_validator_that_doesnt_accept_that_key(self):
            self.client_secret_key_validator = Mock()
            self.client_secret_key_validator.validate.side_effect = InvalidEntityException(
                    source='client_secret_key',
                    code='invalid',
                    message='Invalid client secret key')
            return self

        def given_a_person_repo_that_returns_a_person(self):
            self.person = Person(id='3')
            self.person_repo = Mock()
            self.person_repo.create_guest_person.return_value = self.person
            return self

        def given_an_auth_token_repo_that_returns_a_token(self):
            self.auth_token = AuthToken(person_id='3', access_token='A', refresh_token='R')
            self.auth_token_repo = Mock()
            self.auth_token_repo.create_auth_token.return_value = self.auth_token
            return self

        def when_execute_interactor(self):
            try:
                interactor = CreateGuestPersonAndReturnAuthToken(
                        client_secret_key_validator=self.client_secret_key_validator,
                        person_repo=self.person_repo,
                        auth_token_repo=self.auth_token_repo)
                self.result = interactor.set_params(client_secret_key=self.client_secret_key).execute()
            except Exception as e:
                self.error = e
            return self

        def then_response_should_be_that_token(self):
            assert self.result == self.auth_token
            return self

        def then_should_raise_invalid_entity_exception(self):
            assert type(self.error) is InvalidEntityException
            assert self.error.source == 'client_secret_key'
            assert self.error.code == 'invalid'
            return self

        def then_client_secret_key_should_be_validated(self):
            self.client_secret_key_validator.validate.assert_called_once_with(client_secret_key=self.client_secret_key)
            return self

        def then_person_repo_create_guest_person_should_be_called(self):
            self.person_repo.create_guest_person.assert_called_once()
            return self

        def then_person_repo_create_guest_person_should_not_be_called(self):
            self.person_repo.create_guest_person.assert_not_called()
            return self

        def then_create_auth_token_should_be_called_with_returned_person_id(self):
            self.auth_token_repo.create_auth_token.assert_called_once_with(person_id=self.person.id)
            return self

        def then_create_auth_token_should_not_be_called(self):
            self.auth_token_repo.create_auth_token.assert_not_called()
            return self
