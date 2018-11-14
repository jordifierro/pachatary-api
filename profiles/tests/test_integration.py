import json
import urllib.parse

from django.test import TestCase
from django.test import Client
from django.urls import reverse

from people.models import ORMPerson, ORMAuthToken, ORMBlock
from profiles.models import ORMProfile


class GetProfileTestCase(TestCase):

    def test_returns_profile(self):
        GetProfileTestCase.ScenarioMaker() \
                .given_a_person_with_auth_token() \
                .given_a_profile('uuu') \
                .when_get_is_called_for_profile('uuu') \
                .then_response_should_be_profile_and_200()

    def test_blocked_profile_returns_exception(self):
        GetProfileTestCase.ScenarioMaker() \
                .given_a_person_with_auth_token() \
                .given_a_blocked_person_with_profile('blocked') \
                .when_get_is_called_for_profile('blocked') \
                .then_response_should_be_exception_and_403()

    class ScenarioMaker:

        def given_a_person_with_auth_token(self):
            self.orm_person = ORMPerson.objects.create()
            self.orm_auth_token = ORMAuthToken.objects.create(person_id=self.orm_person.id)
            return self

        def given_a_profile(self, username):
            self.profile = ORMProfile.objects.create(person=self.orm_person, username=username, bio='b')
            return self

        def given_a_blocked_person_with_profile(self, username):
            self.blocked_person = ORMPerson.objects.create()
            ORMProfile.objects.create(person=self.blocked_person, username=username, bio='b')
            ORMBlock.objects.create(creator_id=self.orm_person.id, target_id=self.blocked_person.id)
            return self

        def when_get_is_called_for_profile(self, username):
            client = Client()
            auth_headers = {'HTTP_AUTHORIZATION': 'Token {}'.format(self.orm_auth_token.access_token), }
            self.response = client.get(reverse('profile', args=[username]), **auth_headers)
            return self

        def then_response_should_be_profile_and_200(self):
            assert json.loads(self.response.content) == {
                        'username': self.profile.username,
                        'bio': self.profile.bio,
                        'picture': None,
                        'is_me': True,
                    }
            assert self.response.status_code == 200
            return self

        def then_response_should_be_exception_and_403(self):
            assert json.loads(self.response.content) == {
                    'error': {
                        'source': 'content',
                        'code': 'blocked',
                        'message': 'Content is blocked'
                    }
                }
            assert self.response.status_code == 403
            return self


class ModifyProfileTestCase(TestCase):

    def test_returns_profile(self):
        ModifyProfileTestCase.ScenarioMaker() \
                .given_a_person_with_auth_token() \
                .given_a_profile() \
                .when_patch_is_called_for_profile(bio='new bio') \
                .then_response_should_be_profile_and_200(bio='new bio')

    class ScenarioMaker:

        def given_a_person_with_auth_token(self):
            self.orm_person = ORMPerson.objects.create()
            self.orm_auth_token = ORMAuthToken.objects.create(person_id=self.orm_person.id)
            return self

        def given_a_profile(self):
            self.profile = ORMProfile.objects.create(person=self.orm_person, username='a', bio='b')
            return self

        def when_patch_is_called_for_profile(self, bio):
            client = Client()
            auth_headers = {'HTTP_AUTHORIZATION': 'Token {}'.format(self.orm_auth_token.access_token), }
            self.response = client.patch(reverse('profile', args=['self']),
                                         urllib.parse.urlencode({'bio': bio}),
                                         content_type='application/x-www-form-urlencoded', **auth_headers)
            return self

        def then_response_should_be_profile_and_200(self, bio):
            assert json.loads(self.response.content) == {
                        'username': self.profile.username,
                        'bio': bio,
                        'picture': None,
                        'is_me': True,
                    }
            assert self.response.status_code == 200
            return self
