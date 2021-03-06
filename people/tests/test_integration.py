import json
import urllib.parse
import uuid

from django.conf import settings
from django.test import TestCase, Client
from django.urls import reverse
from django.core import mail
from django.template.loader import get_template

from people.models import ORMAuthToken, ORMPerson, ORMConfirmationToken, ORMLoginToken, ORMBlock
from profiles.models import ORMProfile
from experiences.models import ORMExperience, ORMSave


class CreatePersonTestCase(TestCase):

    def test_creates_guest_person_and_returns_auth_token(self):
        CreatePersonTestCase._ScenarioMaker() \
                .given_a_client_secret_key() \
                .when_people_post_is_called_with_that_client_secret_key() \
                .then_response_status_should_be_201() \
                .then_response_body_should_be_an_auth_token() \
                .then_a_person_has_that_auth_token()

    def test_wrong_client_secret_key_returns_error(self):
        CreatePersonTestCase._ScenarioMaker() \
                .given_a_client_secret_key() \
                .when_people_post_is_called_with_other_client_secret_key() \
                .then_response_status_should_be_422() \
                .then_response_body_should_be_an_error() \


    class _ScenarioMaker:

        def __init__(self):
            self.orm_person = None
            self.orm_auth_token = None
            self.response = None
            self.client_secret_key = None

        def given_a_client_secret_key(self):
            self.client_secret_key = "scrt"
            settings.CLIENT_SECRET_KEY = self.client_secret_key
            return self

        def when_people_post_is_called_with_that_client_secret_key(self):
            client = Client()
            self.response = client.post(reverse('people'), {'client_secret_key': self.client_secret_key})
            return self

        def when_people_post_is_called_with_other_client_secret_key(self):
            client = Client()
            self.response = client.post(reverse('people'), {'client_secret_key': 'wrong_key'})
            return self

        def then_response_status_should_be_201(self):
            assert self.response.status_code == 201
            return self

        def then_response_status_should_be_422(self):
            assert self.response.status_code == 422
            return self

        def then_response_body_should_be_an_auth_token(self):
            body = json.loads(self.response.content)
            assert body['access_token'] is not None
            assert body['refresh_token'] is not None
            return self

        def then_response_body_should_be_an_error(self):
            body = json.loads(self.response.content)
            assert body == {
                    'error': {
                        'source': 'client_secret_key',
                        'code': 'invalid',
                        'message': 'Invalid client secret key'
                        }
                    }
            return self

        def then_a_person_has_that_auth_token(self):
            body = json.loads(self.response.content)
            orm_auth_token = ORMAuthToken.objects.get(access_token=body['access_token'],
                                                      refresh_token=body['refresh_token'])
            orm_person = ORMPerson.objects.get(id=orm_auth_token.person_id)
            assert orm_person is not None
            return self


class ModifyPersonTestCase(TestCase):

    def test_modify_person_username_and_email(self):
        ModifyPersonTestCase._ScenarioMaker() \
                .given_a_guest_person_in_db_with_auth_token() \
                .given_a_confirmation_token_for_that_person() \
                .given_another_confirmation_token_for_that_person() \
                .given_a_username() \
                .given_an_email() \
                .when_that_person_call_patch_people_me_with_that_params() \
                .then_response_status_should_be_204() \
                .then_response_body_should_be_empty() \
                .then_person_and_profile_should_be_updated() \
                .then_old_confirmation_tokens_should_be_deleted() \
                .then_ask_confirmation_email_should_be_sent()

    def test_modify_person_username_and_email_twice_has_same_result(self):
        ModifyPersonTestCase._ScenarioMaker() \
                .given_a_guest_person_in_db_with_auth_token() \
                .given_a_confirmation_token_for_that_person() \
                .given_another_confirmation_token_for_that_person() \
                .given_a_username() \
                .given_an_email() \
                .when_that_person_call_patch_people_me_with_that_params() \
                .when_that_person_call_patch_people_me_with_that_params() \
                .then_response_status_should_be_204() \
                .then_response_body_should_be_empty() \
                .then_person_and_profile_should_be_updated() \
                .then_old_confirmation_tokens_should_be_deleted() \
                .then_ask_confirmation_email_should_be_sent(last=1)

    def test_already_email_confirmed_returns_conflict(self):
        ModifyPersonTestCase._ScenarioMaker() \
                .given_an_email_confirmed_person() \
                .given_a_username() \
                .given_an_email() \
                .when_that_person_call_patch_people_me_with_that_params() \
                .then_response_status_should_be_409() \
                .then_response_body_should_be_conflict_error() \
                .then_person_not_should_be_updated() \
                .then_ask_confirmation_email_should_not_be_sent()

    def test_already_used_mail_returns_error(self):
        ModifyPersonTestCase._ScenarioMaker() \
                .given_a_guest_person_in_db_with_auth_token() \
                .given_an_email() \
                .given_a_username() \
                .given_another_confirmed_person_with_that_email() \
                .when_that_person_call_patch_people_me_with_that_params() \
                .then_response_body_should_be_422_with_invalid_email() \
                .then_person_not_should_be_updated() \
                .then_ask_confirmation_email_should_not_be_sent()

    class _ScenarioMaker:

        def __init__(self):
            self.orm_person = None
            self.orm_confirmation_token = None
            self.orm_confirmation_token_2 = None
            self.username = None
            self.email = None
            self.response = None

        def given_a_guest_person_in_db_with_auth_token(self):
            self.orm_person = ORMPerson.objects.create()
            self.orm_auth_token = ORMAuthToken.objects.create(person_id=self.orm_person.id)
            return self

        def given_an_email_confirmed_person(self):
            self.orm_person = ORMPerson.objects.create(email='e@m.c', is_email_confirmed=True)
            self.orm_auth_token = ORMAuthToken.objects.create(person_id=self.orm_person.id)
            return self

        def given_a_confirmation_token_for_that_person(self):
            self.orm_confirmation_token = ORMConfirmationToken.objects.create(person_id=self.orm_person.id)
            return self

        def given_another_confirmation_token_for_that_person(self):
            self.orm_confirmation_token_2 = ORMConfirmationToken.objects.create(person_id=self.orm_person.id)
            return self

        def given_another_confirmed_person_with_that_email(self):
            ORMPerson.objects.create(email=self.email, is_email_confirmed=True)
            return self

        def given_a_username(self):
            self.username = 'usr.nm'
            return self

        def given_an_email(self):
            self.email = 'usr@m.c'
            return self

        def when_that_person_call_patch_people_me_with_that_params(self):
            client = Client()
            auth_headers = {'HTTP_AUTHORIZATION': 'Token {}'.format(self.orm_auth_token.access_token)}
            self.response = client.patch(reverse('person'),
                                         urllib.parse.urlencode({'username': self.username, 'email': self.email}),
                                         content_type='application/x-www-form-urlencoded',
                                         **auth_headers)
            return self

        def then_response_status_should_be_204(self):
            assert self.response.status_code == 204
            return self

        def then_response_body_should_be_empty(self):
            assert len(self.response.content) == 0
            return self

        def then_person_and_profile_should_be_updated(self):
            orm_updated_person = ORMPerson.objects.get(id=self.orm_person.id)
            assert orm_updated_person.email == self.email
            assert orm_updated_person.is_email_confirmed is False

            orm_profile = ORMProfile.objects.get(person_id=self.orm_person.id)
            assert orm_profile.username == self.username

            return self

        def then_old_confirmation_tokens_should_be_deleted(self):
            assert not ORMConfirmationToken.objects.filter(token=self.orm_confirmation_token.token).exists()
            assert not ORMConfirmationToken.objects.filter(token=self.orm_confirmation_token_2.token).exists()
            return self

        def then_ask_confirmation_email_should_be_sent(self, last=0):
            assert mail.outbox[last].subject == 'Pachatary account confirmation'
            confirmation_token = ORMConfirmationToken.objects.get(person_id=self.orm_person.id).token
            confirmation_url = '{}/redirects/people/me/email-confirmation?token={}'.format(settings.PUBLIC_DOMAIN,
                                                                                           confirmation_token)
            context_params = {'username': self.username, 'confirmation_url': confirmation_url}
            plain_text_message = get_template('ask_confirmation_email.txt').render(context_params)
            html_message = get_template('ask_confirmation_email.html').render(context_params)
            assert mail.outbox[last].body == plain_text_message
            assert mail.outbox[last].from_email == settings.EMAIL_HOST_ORIGIN
            assert mail.outbox[last].to == [self.email, ]
            assert mail.outbox[last].alternatives[0][0] == html_message
            return self

        def then_response_status_should_be_409(self):
            assert self.response.status_code == 409
            return self

        def then_response_body_should_be_conflict_error(self):
            body = json.loads(self.response.content)
            assert body == {
                    'error': {
                        'source': 'person',
                        'code': 'already_registered',
                        'message': 'Person already registered'
                        }
                    }
            return self

        def then_response_body_should_be_422_with_invalid_email(self):
            body = json.loads(self.response.content)
            assert body == {
                    'error': {
                        'source': 'email',
                        'code': 'not_allowed',
                        'message': 'Email not allowed'
                        }
                    }
            return self

        def then_person_not_should_be_updated(self):
            orm_updated_person = ORMPerson.objects.get(id=self.orm_person.id)
            assert orm_updated_person.email != self.email
            assert orm_updated_person.is_email_confirmed == self.orm_person.is_email_confirmed
            return self

        def then_ask_confirmation_email_should_not_be_sent(self):
            assert len(mail.outbox) == 0
            return self


class PostEmailConfirmationTestCase(TestCase):

    def test_post_email_confirmations_confirms_person_email(self):
        PostEmailConfirmationTestCase.ScenarioMaker() \
                .given_an_unconfirmed_registered_person() \
                .given_an_auth_token_for_that_person() \
                .given_a_confirmation_token_for_that_person() \
                .when_post_email_confirmation() \
                .then_response_should_be_204() \
                .then_person_should_have_is_email_confirmed_true() \
                .then_confirmation_token_should_be_removed()

    def test_post_email_confirmation_with_invalid_token_returns_error(self):
        PostEmailConfirmationTestCase.ScenarioMaker() \
                .given_an_unconfirmed_registered_person() \
                .given_an_auth_token_for_that_person() \
                .given_a_fake_confirmation_token() \
                .when_post_email_confirmation() \
                .then_response_code_should_be_422() \
                .then_response_body_should_be_invalide_token_error() \
                .then_person_should_have_is_email_confirmed_false()

    class ScenarioMaker:

        def __init__(self):
            self.orm_person = None
            self.orm_auth_token = None
            self.orm_confirmation_token = None
            self.result = None

        def given_an_unconfirmed_registered_person(self):
            self.orm_person = ORMPerson.objects.create(email='e@m.c', is_email_confirmed=False)
            return self

        def given_an_auth_token_for_that_person(self):
            self.orm_auth_token = ORMAuthToken.objects.create(person_id=self.orm_person.id)
            return self

        def given_a_confirmation_token_for_that_person(self):
            self.orm_confirmation_token = ORMConfirmationToken.objects.create(person_id=self.orm_person.id)
            self.confirmation_token = self.orm_confirmation_token.token
            return self

        def given_a_fake_confirmation_token(self):
            self.confirmation_token = uuid.uuid4()
            return self

        def when_post_email_confirmation(self):
            client = Client()
            auth_headers = {'HTTP_AUTHORIZATION': 'Token {}'.format(self.orm_auth_token.access_token), }
            self.response = client.post(reverse('email-confirmation'),
                                        urllib.parse.urlencode({'confirmation_token': self.confirmation_token}),
                                        content_type='application/x-www-form-urlencoded',
                                        **auth_headers)
            return self

        def then_response_should_be_204(self):
            self.response.status_code == 204
            assert len(self.response.content) == 0
            return self

        def then_person_should_have_is_email_confirmed_true(self):
            assert ORMPerson.objects.get(id=self.orm_person.id).is_email_confirmed is True
            return self

        def then_confirmation_token_should_be_removed(self):
            assert not ORMConfirmationToken.objects.filter(token=self.orm_confirmation_token.token).exists()
            return self

        def then_response_code_should_be_422(self):
            assert self.response.status_code == 422
            return self

        def then_response_body_should_be_invalide_token_error(self):
            body = json.loads(self.response.content)
            assert body == {
                    'error': {
                        'source': 'confirmation_token',
                        'code': 'invalid',
                        'message': 'Invalid confirmation token'
                        }
                    }
            return self

        def then_person_should_have_is_email_confirmed_false(self):
            assert ORMPerson.objects.get(id=self.orm_person.id).is_email_confirmed is False
            return self


class LoginEmailTestCase(TestCase):

    def test_login_email(self):
        LoginEmailTestCase.ScenarioMaker() \
                .given_an_email_confirmed_person() \
                .when_anonymous_call_with_person_email_login_email() \
                .then_response_status_should_be_empty_body_and_204() \
                .then_login_token_should_be_created_for_that_person() \
                .then_login_email_should_be_sent()

    class ScenarioMaker:

        def __init__(self):
            self.orm_person = None
            self.response = None

        def given_an_email_confirmed_person(self):
            self.orm_person = ORMPerson.objects.create(email='e@m.c', is_email_confirmed=True)
            ORMProfile.objects.create(person_id=self.orm_person.id, username='u')
            return self

        def when_anonymous_call_with_person_email_login_email(self):
            client = Client()
            headers = {'HTTP_ACCEPT_LANGUAGE': 'es'}
            self.response = client.post(reverse('login-email'),
                                        urllib.parse.urlencode({'email': self.orm_person.email}),
                                        content_type='application/x-www-form-urlencoded',
                                        **headers)
            return self

        def then_response_status_should_be_empty_body_and_204(self):
            assert len(self.response.content) == 0
            assert self.response.status_code == 204
            return self

        def then_login_token_should_be_created_for_that_person(self):
            assert len(ORMLoginToken.objects.filter(person_id=self.orm_person.id)) == 1
            return self

        def then_login_email_should_be_sent(self):
            assert mail.outbox[0].subject == 'Pachatary login'
            login_token = ORMLoginToken.objects.get(person_id=self.orm_person.id).token
            login_url = '{}/redirects/people/me/login?token={}'.format(settings.PUBLIC_DOMAIN, login_token)
            context_params = {'username': self.orm_person.profile.username, 'login_url': login_url}
            plain_text_message = get_template('login_email.txt').render(context_params)
            html_message = get_template('login_email.html').render(context_params)
            assert mail.outbox[0].body == plain_text_message
            assert mail.outbox[0].from_email == settings.EMAIL_HOST_ORIGIN
            assert mail.outbox[0].to == [self.orm_person.email, ]
            assert mail.outbox[0].alternatives[0][0] == html_message
            return self


class LoginTestCase(TestCase):

    def test_login(self):
        LoginTestCase.ScenarioMaker() \
                .given_an_email_confirmed_person_with_auth_token_and_login_token() \
                .when_anonymous_call_login_whith_login_token() \
                .then_response_status_should_be_200() \
                .then_response_content_should_be_auth_token() \
                .then_login_token_should_be_deleted_for_that_person()

    class ScenarioMaker:

        def given_an_email_confirmed_person_with_auth_token_and_login_token(self):
            self.orm_person = ORMPerson.objects.create(email='e@m.c', is_email_confirmed=True)
            self.orm_auth_token = ORMAuthToken.objects.create(person_id=self.orm_person.id)
            self.orm_login_token = ORMLoginToken.objects.create(person_id=self.orm_person.id)
            return self

        def when_anonymous_call_login_whith_login_token(self):
            client = Client()
            self.response = client.post(reverse('login'),
                                        urllib.parse.urlencode({'token': self.orm_login_token.token}),
                                        content_type='application/x-www-form-urlencoded')
            return self

        def then_response_status_should_be_200(self):
            assert self.response.status_code == 200
            return self

        def then_response_content_should_be_auth_token(self):
            assert json.loads(self.response.content) == {
                'access_token': str(self.orm_auth_token.access_token),
                'refresh_token': str(self.orm_auth_token.refresh_token)
            }
            return self

        def then_login_token_should_be_deleted_for_that_person(self):
            assert len(ORMLoginToken.objects.filter(person_id=self.orm_person.id)) == 0
            return self


class BlockTestCase(TestCase):

    def test_block(self):
        BlockTestCase.ScenarioMaker() \
                .given_a_person() \
                .given_a_person() \
                .given_an_experience(person=2) \
                .given_a_save_experience(person=1, experience=1) \
                .when_block(logged_person=1, target=2) \
                .then_response_status_should_be_empty_body_and_201() \
                .then_save_should_not_exist(person=1, experience=1) \
                .then_block_should_be_created(creator=1, target=2)

    class ScenarioMaker:

        def __init__(self):
            self.persons = []
            self.experiences = []

        def given_a_person(self):
            self.persons.append(ORMPerson.objects.create(email='e@m.c{}'.format(len(self.persons)),
                                                         is_email_confirmed=True))
            ORMProfile.objects.create(person_id=self.persons[len(self.persons)-1].id,
                                      username='u.s_r{}'.format(len(self.persons)), bio='b')
            return self

        def given_an_experience(self, person):
            self.experiences.append(ORMExperience.objects.create(title='t', description='d',
                                                                 author_id=self.persons[person-1].id))
            return self

        def given_a_save_experience(self, person, experience):
            ORMSave.objects.create(person=self.persons[person-1], experience=self.experiences[experience-1])
            return self

        def when_block(self, logged_person, target):
            client = Client()
            orm_auth_token = ORMAuthToken.objects.create(person_id=self.persons[logged_person-1].id)
            auth_headers = {'HTTP_AUTHORIZATION': 'Token {}'.format(orm_auth_token.access_token), }
            self.response = client.post(reverse('person-block', args=[str(self.persons[target-1].profile.username)]),
                                        **auth_headers)
            return self

        def then_response_status_should_be_empty_body_and_201(self):
            assert len(self.response.content) == 0
            assert self.response.status_code == 201
            return self

        def then_save_should_not_exist(self, person, experience):
            assert ORMSave.objects.filter(person_id=self.persons[person-1].id,
                                          experience_id=self.experiences[experience-1].id).exists() is False
            return self

        def then_block_should_be_created(self, creator, target):
            assert ORMBlock.objects.filter(creator_id=self.persons[creator-1].id,
                                           target_id=self.persons[target-1].id)
            return self
