from mock import Mock, call

from pachatary.exceptions import InvalidEntityException, EntityDoesNotExistException, ConflictException, \
        NoLoggedException
from people.entities import Person, AuthToken
from people.interactors import CreateGuestPersonAndReturnAuthTokenInteractor, AuthenticateInteractor, \
        RegisterUsernameAndEmailInteractor, ConfirmEmailInteractor, LoginEmailInteractor, LoginInteractor, \
        BlockInteractor
from profiles.entities import Profile
from experiences.entities import Experience
from experiences.interactors import SaveUnsaveExperienceInteractor


class TestCreateGuestPersonAndReturnAuthToken:

    def test_creates_guest_person_and_returns_auth_token(self):
        TestCreateGuestPersonAndReturnAuthToken._ScenarioMaker() \
                .given_a_client_secret_key() \
                .given_a_client_secret_key_validator_that_accepts_that_key() \
                .given_a_person_repo_that_returns_a_person() \
                .given_an_auth_token_repo_that_returns_a_token() \
                .when_execute_interactor() \
                .then_result_should_be_that_token() \
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

    class _ScenarioMaker:

        def __init__(self):
            self.person = None
            self.auth_token = None
            self.person_repo = None
            self.auth_token_repo = None
            self.result = None
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
                interactor = CreateGuestPersonAndReturnAuthTokenInteractor(
                        client_secret_key_validator=self.client_secret_key_validator,
                        person_repo=self.person_repo,
                        auth_token_repo=self.auth_token_repo)
                self.result = interactor.set_params(client_secret_key=self.client_secret_key).execute()
            except Exception as e:
                self.error = e
            return self

        def then_result_should_be_that_token(self):
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


class TestAuthenticateInteractor:

    def test_correct_access_token_returns_person_id(self):
        TestAuthenticateInteractor.ScenarioMaker() \
                .given_an_access_token() \
                .given_an_auth_token() \
                .given_an_auth_repo_that_returns_that_auth_token() \
                .when_authenticate_interactor_is_executed() \
                .then_should_call_repo_get_auth_token_with_access_token() \
                .then_should_return_auth_token_person_id()

    def test_wrong_access_token_returns_none(self):
        TestAuthenticateInteractor.ScenarioMaker() \
                .given_an_access_token() \
                .given_an_auth_repo_that_raises_entity_does_not_exist() \
                .when_authenticate_interactor_is_executed() \
                .then_should_return_none()

    class ScenarioMaker:

        def __init__(self):
            self.result = None
            self.repo = None
            self.access_token = None
            self.auth_token = None

        def given_an_access_token(self):
            self.access_token = 'A_T'
            return self

        def given_an_auth_token(self):
            self.auth_token = AuthToken(person_id='1', access_token='A', refresh_token='R')
            return self

        def given_an_auth_repo_that_returns_that_auth_token(self):
            self.repo = Mock()
            self.repo.get_auth_token.return_value = self.auth_token
            return self

        def given_an_auth_repo_that_raises_entity_does_not_exist(self):
            self.repo = Mock()
            self.repo.get_auth_token.side_effect = EntityDoesNotExistException
            return self

        def when_authenticate_interactor_is_executed(self):
            self.result = AuthenticateInteractor(self.repo).set_params(access_token=self.access_token).execute()
            return self

        def then_should_call_repo_get_auth_token_with_access_token(self):
            self.repo.get_auth_token.assert_called_once_with(access_token=self.access_token)
            return self

        def then_should_return_auth_token_person_id(self):
            assert self.result == self.auth_token.person_id
            return self

        def then_should_return_none(self):
            assert self.result is None
            return self


class TestRegisterUsernameAndEmailInteractor:

    def test_correct_username_and_email_when_profile_doesnt_exist(self):
        TestRegisterUsernameAndEmailInteractor.ScenarioMaker() \
                .given_a_person_validator_that_returns(True) \
                .given_a_person_repo_that_returns_on_get(Person(id='3', email='b', is_email_confirmed=False)) \
                .given_a_person_repo_that_returns_on_update(Person(id='4', email='o', is_email_confirmed=False)) \
                .given_a_profile_validator_that_returns(True) \
                .given_a_profile_repo_that_returns_on_get(False) \
                .given_a_confirmation_token_repo_that_returns('KT') \
                .when_execute(logged_person_id='1', username='u', email='e') \
                .then_should_call_person_repo_get_with(id='1') \
                .then_should_call_person_validator_with(Person(id='3', email='e', is_email_confirmed=False)) \
                .then_should_call_profile_repo_get_with(person_id='1', logged_person_id='1') \
                .then_should_call_profile_validator_with(Profile(person_id='1', username='u')) \
                .then_should_call_profile_repo_create_with(Profile(person_id='1', username='u')) \
                .then_should_call_person_repo_update_with(Person(id='3', email='e', is_email_confirmed=False)) \
                .then_should_call_confirmation_token_repo_delete_with(person_id='1') \
                .then_should_call_confirmation_token_repo_create_with(person_id='1') \
                .then_should_call_mailer_with(confirmation_token='KT', username='u', email='e') \
                .then_should_return(True)

    def test_correct_username_and_email_when_profile_exists(self):
        TestRegisterUsernameAndEmailInteractor.ScenarioMaker() \
                .given_a_person_validator_that_returns(True) \
                .given_a_person_repo_that_returns_on_get(Person(id='3', email='b', is_email_confirmed=False)) \
                .given_a_person_repo_that_returns_on_update(Person(id='4', email='o', is_email_confirmed=False)) \
                .given_a_profile_validator_that_returns(True) \
                .given_a_profile_repo_that_returns_on_get(Profile(person_id='7', username='p')) \
                .given_a_confirmation_token_repo_that_returns('KT') \
                .when_execute(logged_person_id='1', username='u', email='e') \
                .then_should_call_person_repo_get_with(id='1') \
                .then_should_call_person_validator_with(Person(id='3', email='e', is_email_confirmed=False)) \
                .then_should_call_profile_repo_get_with(person_id='1', logged_person_id='1') \
                .then_should_call_profile_validator_with(Profile(person_id='7', username='u')) \
                .then_should_call_profile_repo_update_with(Profile(person_id='7', username='u')) \
                .then_should_call_person_repo_update_with(Person(id='3', email='e', is_email_confirmed=False)) \
                .then_should_call_confirmation_token_repo_delete_with(person_id='1') \
                .then_should_call_confirmation_token_repo_create_with(person_id='1') \
                .then_should_call_mailer_with(confirmation_token='KT', username='u', email='e') \
                .then_should_return(True)

    def test_incorrect_email_raises_invalid_entity_exception(self):
        TestRegisterUsernameAndEmailInteractor.ScenarioMaker() \
                .given_a_person_validator_that_returns(
                        error=InvalidEntityException(source='e', code='i', message='m')) \
                .given_a_person_repo_that_returns_on_get(Person(id='3', email='b', is_email_confirmed=False)) \
                .when_execute(logged_person_id='1', username='u', email='e') \
                .then_should_call_person_repo_get_with(id='1') \
                .then_should_call_person_validator_with(Person(id='3', email='e', is_email_confirmed=False)) \
                .then_should_call_profile_repo_get_with(False) \
                .then_should_call_profile_validator_with(False) \
                .then_should_call_profile_repo_update_with(False) \
                .then_should_call_person_repo_update_with(False) \
                .then_should_call_confirmation_token_repo_delete_with(False) \
                .then_should_call_confirmation_token_repo_create_with(False) \
                .then_should_call_mailer_with(False) \
                .then_should_raise(InvalidEntityException(source='e', code='i', message='m'))

    def test_incorrect_username_raises_invalid_entity_exception(self):
        TestRegisterUsernameAndEmailInteractor.ScenarioMaker() \
                .given_a_person_validator_that_returns(True) \
                .given_a_person_repo_that_returns_on_get(Person(id='3', email='b', is_email_confirmed=False)) \
                .given_a_profile_validator_that_returns(
                        error=InvalidEntityException(source='u', code='i', message='m')) \
                .given_a_profile_repo_that_returns_on_get(False) \
                .when_execute(logged_person_id='1', username='u', email='e') \
                .then_should_call_person_repo_get_with(id='1') \
                .then_should_call_person_validator_with(Person(id='3', email='e', is_email_confirmed=False)) \
                .then_should_call_profile_repo_get_with(person_id='1', logged_person_id='1') \
                .then_should_call_profile_validator_with(Profile(person_id='1', username='u')) \
                .then_should_call_profile_repo_update_with(False) \
                .then_should_call_person_repo_update_with(False) \
                .then_should_call_confirmation_token_repo_delete_with(False) \
                .then_should_call_confirmation_token_repo_create_with(False) \
                .then_should_call_mailer_with(False) \
                .then_should_raise(InvalidEntityException(source='u', code='i', message='m'))

    def test_cannot_register_once_email_is_confirmed(self):
        TestRegisterUsernameAndEmailInteractor.ScenarioMaker() \
                .given_a_person_validator_that_returns(True) \
                .given_a_person_repo_that_returns_on_get(Person(id='3', email='b', is_email_confirmed=True)) \
                .when_execute(logged_person_id='1', username='u', email='e') \
                .then_should_call_person_repo_get_with(id='1') \
                .then_should_call_person_validator_with(False) \
                .then_should_call_profile_repo_get_with(False) \
                .then_should_call_profile_validator_with(False) \
                .then_should_call_profile_repo_update_with(False) \
                .then_should_call_person_repo_update_with(False) \
                .then_should_call_confirmation_token_repo_delete_with(False) \
                .then_should_call_confirmation_token_repo_create_with(False) \
                .then_should_call_mailer_with(False) \
                .then_should_raise(
                        ConflictException(source='person', code='already_registered',
                                          message='Person already registered'))

    def test_no_logged_person_id_raises_unauthorized(self):
        TestRegisterUsernameAndEmailInteractor.ScenarioMaker() \
                .when_execute(logged_person_id=None, username='u', email='e') \
                .then_should_call_person_repo_get_with(False) \
                .then_should_call_person_validator_with(False) \
                .then_should_call_profile_repo_get_with(False) \
                .then_should_call_profile_validator_with(False) \
                .then_should_call_profile_repo_update_with(False) \
                .then_should_call_person_repo_update_with(False) \
                .then_should_call_confirmation_token_repo_delete_with(False) \
                .then_should_call_confirmation_token_repo_create_with(False) \
                .then_should_call_mailer_with(False) \
                .then_should_raise(NoLoggedException())

    class ScenarioMaker:

        def __init__(self):
            self.person_validator = Mock()
            self.person_repo = Mock()
            self.profile_validator = Mock()
            self.profile_repo = Mock()
            self.confirmation_token_repo = Mock()
            self.mailer_service = Mock()

        def given_a_person_validator_that_returns(self, is_correct=False, error=None):
            if not is_correct:
                self.person_validator.validate.side_effect = error
            else:
                self.person_validator.validate.return_value = True
            return self

        def given_a_person_repo_that_returns_on_get(self, person):
            if person is False:
                self.person_repo.get_person.side_effect = EntityDoesNotExistException()
            else:
                self.person_repo.get_person.return_value = person
            return self

        def given_a_person_repo_that_returns_on_update(self, person):
            self.person_repo.update_person.return_value = person
            return self

        def given_a_profile_validator_that_returns(self, is_correct=False, error=None):
            if not is_correct:
                self.profile_validator.validate.side_effect = error
            else:
                self.profile_validator.validate.return_value = True
            return self

        def given_a_profile_repo_that_returns_on_get(self, profile):
            if profile is False:
                self.profile_repo.get_profile.side_effect = EntityDoesNotExistException()
            else:
                self.profile_repo.get_profile.return_value = profile
            return self

        def given_a_confirmation_token_repo_that_returns(self, confirmation_token):
            self.confirmation_token_repo.create_confirmation_token.return_value = confirmation_token
            return self

        def when_execute(self, logged_person_id, username, email):
            try:
                self.result = RegisterUsernameAndEmailInteractor(
                        person_repo=self.person_repo, person_validator=self.person_validator,
                        profile_repo=self.profile_repo, profile_validator=self.profile_validator,
                        confirmation_token_repo=self.confirmation_token_repo,
                        mailer_service=self.mailer_service) \
                    .set_params(logged_person_id=logged_person_id, username=username, email=email).execute()
            except Exception as e:
                self.error = e
            return self

        def then_should_call_person_repo_get_with(self, id):
            if id is False:
                self.person_repo.get_person.assert_not_called()
            else:
                self.person_repo.get_person.assert_called_once_with(id=id)
            return self

        def then_should_call_person_validator_with(self, person):
            if person is False:
                self.person_validator.validate.assert_not_called()
            else:
                self.person_validator.validate.assert_called_once_with(person)
            return self

        def then_should_call_profile_repo_get_with(self, person_id, logged_person_id=None):
            if person_id is False:
                self.profile_repo.get_profile.assert_not_called()
            else:
                self.profile_repo.get_profile.assert_called_once_with(person_id=person_id,
                                                                      logged_person_id=logged_person_id)
            return self

        def then_should_call_profile_validator_with(self, profile):
            if profile is False:
                self.profile_validator.validate.assert_not_called()
            else:
                self.profile_validator.validate.assert_called_once_with(profile)
            return self

        def then_should_call_profile_repo_create_with(self, profile):
            if profile is False:
                self.profile_repo.create_profile.assert_not_called()
            else:
                self.profile_repo.create_profile.assert_called_once_with(profile)
            return self

        def then_should_call_profile_repo_update_with(self, profile):
            if profile is False:
                self.profile_repo.update_profile.assert_not_called()
            else:
                self.profile_repo.update_profile.assert_called_once_with(profile)
            return self

        def then_should_call_person_repo_update_with(self, person):
            if person is False:
                self.person_repo.update_person.assert_not_called()
            else:
                self.person_repo.update_person.assert_called_once_with(person)
            return self

        def then_should_call_confirmation_token_repo_delete_with(self, person_id):
            if person_id is False:
                self.confirmation_token_repo.delete_confirmation_tokens.assert_not_called()
            else:
                self.confirmation_token_repo.delete_confirmation_tokens.assert_called_once_with(person_id=person_id)
            return self

        def then_should_call_confirmation_token_repo_create_with(self, person_id):
            if person_id is False:
                self.confirmation_token_repo.create_confirmation_token.assert_not_called()
            else:
                self.confirmation_token_repo.create_confirmation_token.assert_called_once_with(person_id=person_id)
            return self

        def then_should_call_mailer_with(self, confirmation_token, username=None, email=None):
            if confirmation_token is False:
                self.mailer_service.send_ask_confirmation_mail.assert_not_called()
            else:
                self.mailer_service.send_ask_confirmation_mail.assert_called_once_with(
                        confirmation_token=confirmation_token, username=username, email=email)
            return self

        def then_should_return(self, result):
            assert self.result == result
            return self

        def then_should_raise(self, error):
            assert self.error == error
            return self


class TestConfirmEmailInteractor:

    def test_confirm_email_returns_person_confirmed(self):
        TestConfirmEmailInteractor.ScenarioMaker() \
                .given_a_logged_person_id() \
                .given_a_confirmation_token() \
                .given_a_confirmation_token_repo_that_returns_that_confirmation_token() \
                .given_an_updated_person() \
                .given_a_person() \
                .given_a_person_repo_that_returns_those_persons_on_get_and_update() \
                .when_confirm_email_interactor_is_executed() \
                .then_should_call_confirmation_token_repo_get_person_id_with_confirmation_token() \
                .then_should_delete_all_confirmation_tokens_for_that_person() \
                .then_should_call_person_repo_get() \
                .then_should_call_person_repo_update_with_is_email_confirmed_true() \
                .then_should_return_true()

    def test_unauthenticated_raises_unauthorized(self):
        TestConfirmEmailInteractor.ScenarioMaker() \
                .when_confirm_email_interactor_is_executed() \
                .then_should_raise_unauthorized() \
                .then_should_not_delete_all_confirmation_tokens_for_that_person() \
                .then_should_not_call_person_repo_update()

    def test_no_confirmation_token_raises_unauthorized(self):
        TestConfirmEmailInteractor.ScenarioMaker() \
                .given_a_logged_person_id() \
                .given_a_confirmation_token_repo_that_raises_entity_does_not_exist() \
                .when_confirm_email_interactor_is_executed() \
                .then_should_raise_invalid_params_for_wrong_confirmation_token() \
                .then_should_not_delete_all_confirmation_tokens_for_that_person() \
                .then_should_not_call_person_repo_update()

    def test_not_coincident_person_id_raises_unauthorized(self):
        TestConfirmEmailInteractor.ScenarioMaker() \
                .given_a_logged_person_id() \
                .given_a_confirmation_token_repo_that_returns_another_person_id() \
                .when_confirm_email_interactor_is_executed() \
                .then_should_raise_invalid_params_for_wrong_confirmation_token() \
                .then_should_not_delete_all_confirmation_tokens_for_that_person() \
                .then_should_not_call_person_repo_update()

    class ScenarioMaker:

        def __init__(self):
            self.result = None
            self.error = None
            self.updated_person = None
            self.person = None
            self.logged_person_id = None
            self.confirmation_token = None
            self.confirmation_token_repo = Mock()
            self.person_repo = Mock()

        def given_a_logged_person_id(self):
            self.logged_person_id = '2'
            return self

        def given_a_confirmation_token(self):
            self.confirmation_token = 'ABC'
            return self

        def given_a_confirmation_token_repo_that_returns_that_confirmation_token(self):
            self.confirmation_token_repo.get_person_id.return_value = self.logged_person_id
            return self

        def given_a_confirmation_token_repo_that_returns_another_person_id(self):
            self.confirmation_token_repo.get_person_id.return_value = '99'
            return self

        def given_a_confirmation_token_repo_that_raises_entity_does_not_exist(self):
            self.confirmation_token_repo.get_person_id.side_effect = EntityDoesNotExistException()
            return self

        def given_a_person(self):
            self.person = Person(id='4', email='e@m.c', is_email_confirmed=False)
            return self

        def given_an_updated_person(self):
            self.updated_person = Person(id='4', email='e@m.c', is_email_confirmed=True)
            return self

        def given_a_person_repo_that_returns_those_persons_on_get_and_update(self):
            self.person_repo.update_person.return_value = self.updated_person
            self.person_repo.get_person.return_value = self.person
            return self

        def when_confirm_email_interactor_is_executed(self):
            try:
                interactor = ConfirmEmailInteractor(confirmation_token_repo=self.confirmation_token_repo,
                                                    person_repo=self.person_repo)
                self.result = interactor.set_params(logged_person_id=self.logged_person_id,
                                                    confirmation_token=self.confirmation_token).execute()
            except Exception as e:
                self.error = e
            return self

        def then_should_call_confirmation_token_repo_get_person_id_with_confirmation_token(self):
            self.confirmation_token_repo.get_person_id \
                    .assert_called_once_with(confirmation_token=self.confirmation_token)
            return self

        def then_should_delete_all_confirmation_tokens_for_that_person(self):
            self.confirmation_token_repo.delete_confirmation_tokens \
                    .assert_called_once_with(person_id=self.logged_person_id)
            return self

        def then_should_call_person_repo_get(self):
            self.person_repo.get_person.assert_called_once_with(id=self.logged_person_id)
            return self

        def then_should_call_person_repo_update_with_is_email_confirmed_true(self):
            update_person = Person(id=self.person.id, email=self.person.email, is_email_confirmed=True)
            self.person_repo.update_person.assert_called_once_with(update_person)
            return self

        def then_should_return_true(self):
            assert self.result is True
            return self

        def then_should_raise_unauthorized(self):
            assert type(self.error) is NoLoggedException
            return self

        def then_should_not_delete_all_confirmation_tokens_for_that_person(self):
            self.confirmation_token_repo.delete_confirmation_tokens.assert_not_called()
            return self

        def then_should_not_call_person_repo_update(self):
            self.person_repo.update_person.assert_not_called()
            return self

        def then_should_raise_invalid_params_for_wrong_confirmation_token(self):
            assert type(self.error) is InvalidEntityException
            assert self.error.source == 'confirmation_token'
            assert self.error.code == 'invalid'
            assert str(self.error) == 'Invalid confirmation token'
            return self


class TestLoginEmailInteractor:

    def test_when_email_doesnt_exists(self):
        TestLoginEmailInteractor.ScenarioMaker() \
                .given_an_email() \
                .given_a_person_repo_that_raises_entity_does_not_exist() \
                .when_login_email_interactor_executed() \
                .then_should_call_get_person_repo_with_the_email() \
                .then_should_not_call_login_token_repo() \
                .then_should_not_call_mailer_service()

    def test_when_email_has_not_been_confirmed(self):
        TestLoginEmailInteractor.ScenarioMaker() \
                .given_an_email() \
                .given_a_person_repo_that_returns_person_without_confirmed_email() \
                .when_login_email_interactor_executed() \
                .then_should_call_get_person_repo_with_the_email() \
                .then_should_not_call_login_token_repo() \
                .then_should_not_call_mailer_service()

    def test_success(self):
        TestLoginEmailInteractor.ScenarioMaker() \
                .given_an_email() \
                .given_a_person() \
                .given_a_person_repo_that_returns_that_person() \
                .given_a_profile() \
                .given_a_profile_repo_that_returns_that_profile() \
                .given_a_login_token() \
                .given_a_login_token_repo_that_returns_that_token() \
                .when_login_email_interactor_executed() \
                .then_should_call_get_person_repo_with_the_email() \
                .then_should_call_get_profile_repo_with_the_person_id() \
                .then_should_call_delete_login_tokens_with_person_id() \
                .then_should_call_create_login_token_with_person_id() \
                .then_should_send_mail_with_token_username_to_person_email()

    class ScenarioMaker:

        def __init__(self):
            self.person_repo = Mock()
            self.profile_repo = Mock()
            self.login_token_repo = Mock()
            self.mailer_service = Mock()

        def given_an_email(self):
            self.email = 'asdf@email.com'
            return self

        def given_a_person(self):
            self.person = Person(id='8', email='e', is_email_confirmed=True)
            return self

        def given_a_profile(self):
            self.profile = Profile(person_id=self.person.id, username='u')
            return self

        def given_a_login_token(self):
            self.login_token = 'ABXZ'
            return self

        def given_a_person_repo_that_raises_entity_does_not_exist(self):
            self.person_repo.get_person.side_effect = EntityDoesNotExistException()
            return self

        def given_a_person_repo_that_returns_person_without_confirmed_email(self):
            self.person_repo.get_person.return_value = Person(id='5', is_email_confirmed=False)
            return self

        def given_a_person_repo_that_returns_that_person(self):
            self.person_repo.get_person.return_value = self.person
            return self

        def given_a_profile_repo_that_returns_that_profile(self):
            self.profile_repo.get_profile.return_value = self.profile
            return self

        def given_a_login_token_repo_that_returns_that_token(self):
            self.login_token_repo.create_login_token.return_value = self.login_token
            return self

        def when_login_email_interactor_executed(self):
            try:
                interactor = LoginEmailInteractor(login_token_repo=self.login_token_repo,
                                                  person_repo=self.person_repo,
                                                  profile_repo=self.profile_repo,
                                                  mailer_service=self.mailer_service)
                self.result = interactor.set_params(email=self.email).execute()
            except Exception as e:
                self.error = e
            return self

        def then_should_call_get_person_repo_with_the_email(self):
            self.person_repo.get_person.assert_called_once_with(email=self.email)
            return self

        def then_should_call_get_profile_repo_with_the_person_id(self):
            self.profile_repo.get_profile.assert_called_once_with(person_id=self.person.id,
                                                                  logged_person_id=self.person.id)
            return self

        def then_should_not_call_login_token_repo(self):
            self.login_token_repo.delete_login_tokens.assert_not_called()
            self.login_token_repo.create_login_token.assert_not_called()
            return self

        def then_should_not_call_mailer_service(self):
            self.mailer_service.send_login_mail.assert_not_called()
            return self

        def then_should_call_delete_login_tokens_with_person_id(self):
            self.login_token_repo.delete_login_tokens.assert_called_once_with(person_id=self.person.id)
            return self

        def then_should_call_create_login_token_with_person_id(self):
            self.login_token_repo.create_login_token.assert_called_once_with(person_id=self.person.id)
            return self

        def then_should_send_mail_with_token_username_to_person_email(self):
            self.mailer_service.send_login_mail.assert_called_once_with(login_token=self.login_token,
                                                                        username=self.profile.username,
                                                                        email=self.person.email)
            return self


class TestLoginInteractor:

    def test_returns_auth_token_and_person(self):
        TestLoginInteractor.ScenarioMaker() \
                .given_a_login_token() \
                .given_a_person_id() \
                .given_a_login_token_repo_that_returns_that_person_id() \
                .given_a_person() \
                .given_a_person_repo_that_returns_that_person() \
                .given_an_auth_token() \
                .given_an_auth_token_repo_that_returns_that_auth_token() \
                .when_login_interactor_is_executed() \
                .then_should_call_login_token_repo_get_person_id_with_login_token() \
                .then_should_call_login_token_repo_delete_login_token_with_person_id() \
                .then_should_call_auth_token_repo_get_auth_token_with_person_id() \
                .then_should_return_auth_token()

    class ScenarioMaker:

        def given_a_login_token(self):
            self.login_token = 'tra'
            return self

        def given_a_person_id(self):
            self.person_id = '4'
            return self

        def given_a_login_token_repo_that_returns_that_person_id(self):
            self.login_token_repo = Mock()
            self.login_token_repo.get_person_id.return_value = self.person_id
            return self

        def given_a_person(self):
            self.person = Person(id='9', email='e')
            return self

        def given_a_person_repo_that_returns_that_person(self):
            self.person_repo = Mock()
            self.person_repo.get_person.return_value = self.person
            return self

        def given_an_auth_token(self):
            self.auth_token = AuthToken('9', 'a', 'r')
            return self

        def given_an_auth_token_repo_that_returns_that_auth_token(self):
            self.auth_token_repo = Mock()
            self.auth_token_repo.get_auth_token.return_value = self.auth_token
            return self

        def when_login_interactor_is_executed(self):
            self.result = LoginInteractor(self.person_repo, self.auth_token_repo, self.login_token_repo) \
                    .set_params(login_token=self.login_token).execute()
            return self

        def then_should_call_login_token_repo_get_person_id_with_login_token(self):
            self.login_token_repo.get_person_id.assert_called_once_with(login_token=self.login_token)
            return self

        def then_should_call_login_token_repo_delete_login_token_with_person_id(self):
            self.login_token_repo.delete_login_tokens.assert_called_once_with(person_id=self.person_id)
            return self

        def then_should_call_auth_token_repo_get_auth_token_with_person_id(self):
            self.auth_token_repo.get_auth_token.assert_called_once_with(person_id=self.person_id)
            return self

        def then_should_return_auth_token(self):
            self.result == self.auth_token
            return self


class TestBlockIntearctor:

    def test_block_interactor_raises_not_logged(self):
        TestBlockIntearctor.ScenarioMaker() \
            .given_a_permissions_validator_that_raises_no_logged() \
            .when_block(logged_person_id='4', target_username='blocked') \
            .then_should_call_permissions_validator('4') \
            .then_should_not_call_block() \
            .then_should_raise_no_logged_exception()

    def test_already_blocked_returns_true(self):
        TestBlockIntearctor.ScenarioMaker() \
            .given_a_permissions_validator_that_validates() \
            .given_a_block_repo_that_returns_to_block_exists(True) \
            .given_a_profile_repo_that_returns_profile_with_person_id('33') \
            .when_block(logged_person_id='4', target_username='blocked') \
            .then_should_call_permissions_validator('4') \
            .then_should_get_profile_with(username='blocked', logged_person_id='4') \
            .then_should_call_block_exists('4', '33') \
            .then_should_not_call_block() \
            .then_should_return_true()

    def test_self_block_raises_conflict_exception(self):
        TestBlockIntearctor.ScenarioMaker() \
            .given_a_permissions_validator_that_validates() \
            .given_a_block_repo_that_returns_to_block_exists(False) \
            .given_a_profile_repo_that_returns_profile_with_person_id('4') \
            .when_block(logged_person_id='4', target_username='myself') \
            .then_should_call_permissions_validator('4') \
            .then_should_get_profile_with(username='myself', logged_person_id='4') \
            .then_should_not_call_block() \
            .then_should_raise_conflict_exception()

    def test_block_unsaves_target_id_experiences_block_and_returns_true(self):
        TestBlockIntearctor.ScenarioMaker() \
            .given_a_permissions_validator_that_validates() \
            .given_a_block_repo_that_returns_to_block_exists(False) \
            .given_a_block_repo_that_returns_to_block(True) \
            .given_a_experience_repo_that_returns([
                Experience('t', 'd', id='11', author_id='9'),
                Experience('t', 'd', id='12', author_id='33'),
                Experience('t', 'd', id='13', author_id='9'),
                Experience('t', 'd', id='14', author_id='33'),
                Experience('t', 'd', id='15', author_id='9'),
                Experience('t', 'd', id='16', author_id='9')]) \
            .given_a_profile_repo_that_returns_profile_with_person_id('33') \
            .when_block(logged_person_id='4', target_username='blocked') \
            .then_should_call_permissions_validator('4') \
            .then_should_call_block_exists('4', '33') \
            .then_should_get_saved_experiences('4') \
            .then_should_get_profile_with(username='blocked', logged_person_id='4') \
            .then_should_unsave('4', ['12', '14']) \
            .then_should_call_block('4', '33') \
            .then_should_return_true()

    class ScenarioMaker:

        def __init__(self):
            self.permissions_validator = Mock()
            self.block_repo = Mock()
            self.experience_repo = Mock()
            self.profile_repo = Mock()
            self.unsave_experience_interactor = Mock()
            self.unsave_experience_interactor.set_params.return_value = self.unsave_experience_interactor

        def given_a_permissions_validator_that_validates(self):
            self.permissions_validator.return_value = True
            return self

        def given_a_permissions_validator_that_raises_no_logged(self):
            self.permissions_validator.validate_permissions.side_effect = NoLoggedException()
            return self

        def given_a_block_repo_that_returns_to_block_exists(self, exists):
            self.block_repo.block_exists.return_value = exists
            return self

        def given_a_block_repo_that_returns_to_block(self, exists):
            self.block_repo.block.return_value = exists
            return self

        def given_a_profile_repo_that_returns_profile_with_person_id(self, person_id):
            self.profile_repo.get_profile.return_value = Profile(person_id=person_id)
            return self

        def given_a_experience_repo_that_returns(self, experiences):
            self.experience_repo.get_saved_experiences.return_value = {'results': experiences, 'next_offset': None}
            return self

        def when_block(self, logged_person_id, target_username):
            try:
                self.result = BlockInteractor(permissions_validator=self.permissions_validator,
                                              block_repo=self.block_repo,
                                              experience_repo=self.experience_repo,
                                              profile_repo=self.profile_repo,
                                              save_unsave_experience_interactor=self.unsave_experience_interactor) \
                        .set_params(logged_person_id=logged_person_id, target_username=target_username).execute()
            except Exception as e:
                self.error = e
            return self

        def then_should_call_permissions_validator(self, person_id):
            self.permissions_validator.validate_permissions.assert_called_once_with(logged_person_id=person_id)
            return self

        def then_should_call_block_exists(self, creator_id, target_id):
            self.block_repo.block_exists.assert_called_once_with(creator_id=creator_id, target_id=target_id)
            return self

        def then_should_not_call_block(self):
            self.block_repo.block.assert_not_called()
            return self

        def then_should_get_saved_experiences(self, person_id):
            self.experience_repo.get_saved_experiences.assert_called_once_with(logged_person_id=person_id,
                                                                               offset=0, limit=1000000)
            return self

        def then_should_unsave(self, person_id, experiences_ids):
            self.unsave_experience_interactor.set_params.assert_has_calls(
                [call(action=SaveUnsaveExperienceInteractor.Action.UNSAVE,
                      experience_id=id, logged_person_id=person_id) for id in experiences_ids])
            self.unsave_experience_interactor.execute.assert_has_calls([call() for id in experiences_ids])
            return self

        def then_should_call_block(self, creator_id, target_id):
            self.block_repo.block.assert_called_once_with(creator_id=creator_id, target_id=target_id)
            return self

        def then_should_get_profile_with(self, username, logged_person_id):
            self.profile_repo.get_profile.assert_called_once_with(username=username, logged_person_id=logged_person_id)
            return self

        def then_should_raise_no_logged_exception(self):
            assert type(self.error) is NoLoggedException
            return self

        def then_should_raise_conflict_exception(self):
            assert type(self.error) is ConflictException
            assert self.error == ConflictException(source='person', code='conflict', message='Cannot block yourself')
            return self

        def then_should_return_true(self):
            assert self.result is True
            return self
