import uuid

from django.test import TestCase

from pachatary.exceptions import EntityDoesNotExistException
from people.models import ORMPerson, ORMAuthToken, ORMConfirmationToken, ORMLoginToken
from people.repositories import PersonRepo, AuthTokenRepo, ConfirmationTokenRepo, LoginTokenRepo, BlockRepo
from people.entities import Person


class PersonRepoTestCase(TestCase):

    def test_create_guest_person(self):
        PersonRepoTestCase._ScenarioMaker() \
                .when_create_guest_person() \
                .then_response_should_be_a_guest_person() \
                .then_that_person_should_be_saved_in_db()

    def test_update_person(self):
        PersonRepoTestCase._ScenarioMaker() \
                .given_a_person_in_db() \
                .given_a_person_entity_with_db_person_id() \
                .when_update_person_entity() \
                .then_result_should_be_person_entity() \
                .then_db_person_should_be_same_as_entity()

    def test_get_person(self):
        PersonRepoTestCase._ScenarioMaker() \
                .given_a_person_in_db() \
                .when_get_person_with_her_id() \
                .then_result_should_be_that_person()

    def test_get_person_by_email(self):
        PersonRepoTestCase._ScenarioMaker() \
                .given_a_person_in_db() \
                .when_get_person_with_her_email() \
                .then_result_should_be_that_person()

    class _ScenarioMaker:

        def __init__(self):
            self.response = None
            self.orm_person = None
            self.person = None

        def given_a_person_in_db(self):
            self.orm_person = ORMPerson.objects.create()
            return self

        def given_a_person_entity_with_db_person_id(self):
            self.person = Person(id=str(self.orm_person.id), email='E', is_email_confirmed=True)
            return self

        def when_create_guest_person(self):
            self.result = PersonRepo().create_guest_person()
            return self

        def when_get_person_with_her_id(self):
            self.result = PersonRepo().get_person(id=str(self.orm_person.id))
            return self

        def when_get_person_with_her_email(self):
            self.result = PersonRepo().get_person(email=self.orm_person.email)
            return self

        def when_update_person_entity(self):
            self.result = PersonRepo().update_person(self.person)
            return self

        def then_response_should_be_a_guest_person(self):
            assert self.result.id is not None
            assert self.result.email is None
            assert not self.result.is_email_confirmed
            return self

        def then_that_person_should_be_saved_in_db(self):
            assert ORMPerson.objects.filter(id=self.result.id).exists()
            return self

        def then_result_should_be_person_entity(self):
            assert self.result == self.person
            return self

        def then_db_person_should_be_same_as_entity(self):
            updated_orm_person = ORMPerson.objects.get(id=self.orm_person.id)
            assert updated_orm_person.email == self.person.email
            assert updated_orm_person.is_email_confirmed == self.person.is_email_confirmed
            return self

        def then_result_should_be_that_person(self):
            assert str(self.orm_person.id) == self.result.id
            assert self.orm_person.email == self.result.email
            assert self.orm_person.is_email_confirmed == self.result.is_email_confirmed
            return self


class AuthTokenRepoTestCase(TestCase):

    def test_create_auth_token(self):
        AuthTokenRepoTestCase._ScenarioMaker() \
                .given_a_person() \
                .when_create_auth_token_for_that_person() \
                .then_response_should_be_that_token() \
                .then_that_token_should_be_saved_in_db()

    def test_get_auth_token_from_access_token(self):
        AuthTokenRepoTestCase._ScenarioMaker() \
                .given_a_person() \
                .given_an_auth_token_for_that_person() \
                .when_get_auth_token_with_access_token() \
                .then_should_return_auth_token()

    def test_get_auth_token_from_person_id(self):
        AuthTokenRepoTestCase._ScenarioMaker() \
                .given_a_person() \
                .given_an_auth_token_for_that_person() \
                .when_get_auth_token_with_person_id() \
                .then_should_return_auth_token()

    def test_unexistent_get_auth_token(self):
        AuthTokenRepoTestCase._ScenarioMaker() \
                .when_get_auth_token_with_wrong_access_token() \
                .then_should_raise_entity_does_not_exist()

    class _ScenarioMaker:

        def __init__(self):
            self.person = None
            self.response = None
            self.error = None

        def given_a_person(self):
            self.person = PersonRepo().create_guest_person()
            return self

        def given_an_auth_token_for_that_person(self):
            self.auth_token = AuthTokenRepo().create_auth_token(person_id=self.person.id)
            return self

        def when_get_auth_token_with_access_token(self):
            try:
                self.result = AuthTokenRepo().get_auth_token(access_token=self.auth_token.access_token)
            except Exception as e:
                self.error = e
            return self

        def when_get_auth_token_with_person_id(self):
            try:
                self.result = AuthTokenRepo().get_auth_token(person_id=self.person.id)
            except Exception as e:
                self.error = e
            return self

        def when_get_auth_token_with_wrong_access_token(self):
            try:
                self.result = AuthTokenRepo().get_auth_token(access_token=str(uuid.uuid4()))
            except Exception as e:
                self.error = e
            return self

        def when_create_auth_token_for_that_person(self):
            try:
                self.result = AuthTokenRepo().create_auth_token(person_id=self.person.id)
            except Exception as e:
                self.error = e
            return self

        def then_should_return_auth_token(self):
            assert self.result == self.auth_token
            return self

        def then_response_should_be_that_token(self):
            assert self.result.person_id == self.person.id
            assert type(self.result.access_token) is str
            assert type(self.result.refresh_token) is str
            return self

        def then_that_token_should_be_saved_in_db(self):
            assert ORMAuthToken.objects.filter(person_id=self.result.person_id, access_token=self.result.access_token,
                                               refresh_token=self.result.refresh_token).exists()
            return self

        def then_should_raise_entity_does_not_exist(self):
            assert type(self.error) is EntityDoesNotExistException
            return self


class ConfirmationTokenRepoTestCase(TestCase):

    def test_create_confirmation_token(self):
        ConfirmationTokenRepoTestCase._ScenarioMaker() \
                .given_a_person() \
                .when_create_confirmation_token_for_that_person() \
                .then_should_return_confirmation_token() \
                .then_that_token_should_be_saved_in_db()

    def test_delete_confirmation_tokens_from_person(self):
        ConfirmationTokenRepoTestCase._ScenarioMaker() \
                .given_a_person() \
                .when_create_confirmation_token_for_that_person() \
                .when_create_confirmation_token_for_that_person() \
                .when_create_confirmation_token_for_that_person() \
                .when_delete_confirmation_tokens_for_that_person() \
                .then_response_should_be_true() \
                .then_there_should_be_no_confirmation_tokens_for_that_person()

    def test_get_person_id_from_confirmation_token(self):
        ConfirmationTokenRepoTestCase._ScenarioMaker() \
                .given_a_person() \
                .given_a_confirmation_token_for_that_person() \
                .when_get_person_id_for_that_confirmation_token() \
                .then_response_should_be_person_id()

    def test_get_person_id_when_has_no_tokens(self):
        ConfirmationTokenRepoTestCase._ScenarioMaker() \
                .given_a_random_confirmation_token_not_in_db() \
                .when_get_person_id_for_that_confirmation_token() \
                .then_should_raise_entity_does_not_exist()

    class _ScenarioMaker:

        def __init__(self):
            self.person = None
            self.response = None
            self.error = None

        def given_a_person(self):
            self.person = PersonRepo().create_guest_person()
            return self

        def given_a_confirmation_token_for_that_person(self):
            self.confirmation_token = ConfirmationTokenRepo().create_confirmation_token(person_id=self.person.id)
            return self

        def given_a_random_confirmation_token_not_in_db(self):
            self.confirmation_token = uuid.uuid4()
            return self

        def when_get_person_id_for_that_confirmation_token(self):
            try:
                self.result = ConfirmationTokenRepo().get_person_id(confirmation_token=self.confirmation_token)
            except Exception as e:
                self.error = e
            return self

        def when_create_confirmation_token_for_that_person(self):
            self.result = ConfirmationTokenRepo().create_confirmation_token(person_id=self.person.id)
            return self

        def when_delete_confirmation_tokens_for_that_person(self):
            self.result = ConfirmationTokenRepo().delete_confirmation_tokens(person_id=self.person.id)
            return self

        def then_should_return_confirmation_token(self):
            assert type(self.result) is str
            assert len(self.result) > 0
            return self

        def then_that_token_should_be_saved_in_db(self):
            assert ORMConfirmationToken.objects.filter(person_id=self.person.id, token=self.result).exists()
            return self

        def then_response_should_be_true(self):
            assert self.result is True
            return self

        def then_there_should_be_no_confirmation_tokens_for_that_person(self):
            assert not ORMConfirmationToken.objects.filter(person_id=self.person.id).exists()

        def then_response_should_be_person_id(self):
            assert self.result == self.person.id
            return self

        def then_should_raise_entity_does_not_exist(self):
            assert type(self.error) is EntityDoesNotExistException
            return self


class LoginTokenRepoTestCase(TestCase):

    def test_create_login_token(self):
        LoginTokenRepoTestCase._ScenarioMaker() \
                .given_a_person() \
                .when_create_login_token_for_that_person() \
                .then_should_return_login_token() \
                .then_that_token_should_be_saved_in_db()

    def test_delete_login_tokens_from_person(self):
        LoginTokenRepoTestCase._ScenarioMaker() \
                .given_a_person() \
                .when_create_login_token_for_that_person() \
                .when_create_login_token_for_that_person() \
                .when_create_login_token_for_that_person() \
                .when_delete_login_tokens_for_that_person() \
                .then_response_should_be_true() \
                .then_there_should_be_no_login_tokens_for_that_person()

    def test_get_person_id_from_login_token(self):
        LoginTokenRepoTestCase._ScenarioMaker() \
                .given_a_person() \
                .given_a_login_token_for_that_person() \
                .when_get_person_id_for_that_login_token() \
                .then_response_should_be_person_id()

    def test_get_person_id_when_has_no_tokens(self):
        LoginTokenRepoTestCase._ScenarioMaker() \
                .given_a_random_login_token_not_in_db() \
                .when_get_person_id_for_that_login_token() \
                .then_should_raise_entity_does_not_exist()

    class _ScenarioMaker:

        def __init__(self):
            self.person = None
            self.response = None
            self.error = None

        def given_a_person(self):
            self.person = PersonRepo().create_guest_person()
            return self

        def given_a_login_token_for_that_person(self):
            self.login_token = LoginTokenRepo().create_login_token(person_id=self.person.id)
            return self

        def given_a_random_login_token_not_in_db(self):
            self.login_token = uuid.uuid4()
            return self

        def when_get_person_id_for_that_login_token(self):
            try:
                self.result = LoginTokenRepo().get_person_id(login_token=self.login_token)
            except Exception as e:
                self.error = e
            return self

        def when_create_login_token_for_that_person(self):
            self.result = LoginTokenRepo().create_login_token(person_id=self.person.id)
            return self

        def when_delete_login_tokens_for_that_person(self):
            self.result = LoginTokenRepo().delete_login_tokens(person_id=self.person.id)
            return self

        def then_should_return_login_token(self):
            assert type(self.result) is str
            assert len(self.result) > 0
            return self

        def then_that_token_should_be_saved_in_db(self):
            assert ORMLoginToken.objects.filter(person_id=self.person.id, token=self.result).exists()
            return self

        def then_response_should_be_true(self):
            assert self.result is True
            return self

        def then_there_should_be_no_login_tokens_for_that_person(self):
            assert not ORMLoginToken.objects.filter(person_id=self.person.id).exists()

        def then_response_should_be_person_id(self):
            assert self.result == self.person.id
            return self

        def then_should_raise_entity_does_not_exist(self):
            assert type(self.error) is EntityDoesNotExistException
            return self


class BlockRepoTestCase(TestCase):

    def test_block_exists_returns_true_when_there_is_block(self):
        BlockRepoTestCase.ScenarioMaker() \
            .given_a_person() \
            .given_a_person() \
            .given_a_block(creator=1, target=2) \
            .when_block_exists(creator=1, target=2) \
            .then_result_should_be(True)

    def test_block_exists_returns_false_when_there_is_no_block(self):
        BlockRepoTestCase.ScenarioMaker() \
            .given_a_person() \
            .given_a_person() \
            .when_block_exists(creator=1, target=2) \
            .then_result_should_be(False)

    def test_blocked_people_returns_ids_list(self):
        BlockRepoTestCase.ScenarioMaker() \
            .given_a_person() \
            .given_a_person() \
            .given_a_person() \
            .given_a_person() \
            .given_a_person() \
            .given_a_person() \
            .given_a_block(creator=1, target=2) \
            .given_a_block(creator=1, target=3) \
            .given_a_block(creator=4, target=1) \
            .given_a_block(creator=1, target=5) \
            .given_a_block(creator=1, target=6) \
            .given_a_block(creator=6, target=1) \
            .given_a_block(creator=2, target=3) \
            .when_blocked_people(person=1) \
            .then_result_should_be_ids_from_people([2, 3, 5, 6])

    def test_no_blocked_people_returns_empty_list(self):
        BlockRepoTestCase.ScenarioMaker() \
            .given_a_person() \
            .when_blocked_people(person=1) \
            .then_result_should_be_ids_from_people([])

    class ScenarioMaker:

        def __init__(self):
            self.repo = BlockRepo()
            self.persons = []

        def given_a_person(self):
            self.persons.append(PersonRepo().create_guest_person())
            return self

        def given_a_block(self, creator, target):
            self.repo.block(creator_id=self.persons[creator-1].id,
                            target_id=self.persons[target-1].id)
            return self

        def when_block_exists(self, creator, target):
            self.result = self.repo.block_exists(creator_id=self.persons[creator-1].id,
                                                 target_id=self.persons[target-1].id)
            return self

        def when_blocked_people(self, person):
            self.result = self.repo.get_blocked_people(person_id=self.persons[person-1].id)
            return self

        def then_result_should_be(self, expected_result):
            assert self.result == expected_result
            return self

        def then_result_should_be_ids_from_people(self, people):
            people_ids = [self.persons[person-1].id for person in people]
            assert self.result == people_ids
