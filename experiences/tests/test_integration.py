import json
from elasticsearch.exceptions import NotFoundError
import urllib.parse
from mock import Mock

from django.test import TestCase, TransactionTestCase
from django.test import Client
from django.urls import reverse
from django.conf import settings

from experiences.models import ORMExperience, ORMSave, ORMFlag
from experiences.entities import Experience
from experiences.repositories import ExperienceRepo
from experiences.factories import create_experience_elastic_repo
from experiences.serializers import serialize_multiple_experiences
from people.models import ORMPerson, ORMAuthToken, ORMBlock
from profiles.models import ORMProfile
from scenes.entities import Scene
from profiles.entities import Profile


class ExperiencesTestCase(TestCase):

    def test_mine_experiences_returns_my_experiences(self):
        orm_person = ORMPerson.objects.create()
        orm_auth_token = ORMAuthToken.objects.create(person=orm_person)
        ORMProfile.objects.create(person_id=orm_person.id, username='a', bio='b')
        ORMExperience.objects.create(title='Exp c', description='other description', author=orm_person)
        exp_b = ORMExperience.objects.create(title='Exp b', description='other description', author=orm_person)
        exp_a = ORMExperience.objects.create(title='Exp a', description='some description', author=orm_person)

        client = Client()
        auth_headers = {'HTTP_AUTHORIZATION': 'Token {}'.format(orm_auth_token.access_token), }
        response = client.get("{}?username=self&limit=2".format(reverse('experiences')), **auth_headers)

        assert response.status_code == 200
        body = json.loads(response.content)
        assert body == {
                'results': [
                           {
                               'id': str(exp_a.id),
                               'title': 'Exp a',
                               'description': 'some description',
                               'picture': None,
                               'author_profile': {
                                   'username': 'a',
                                   'bio': 'b',
                                   'picture': None,
                                   'is_me': True,
                                },
                               'is_mine': True,
                               'is_saved': False,
                               'saves_count': 0
                           },
                           {
                               'id': str(exp_b.id),
                               'title': 'Exp b',
                               'description': 'other description',
                               'picture': None,
                               'author_profile': {
                                   'username': 'a',
                                   'bio': 'b',
                                   'picture': None,
                                   'is_me': True,
                                },
                               'is_mine': True,
                               'is_saved': False,
                               'saves_count': 0
                           },
                       ],
                'next_url': 'http://testserver/experiences/?username=self&limit=2&offset=2'
            }

    def test_others_experiences_returns_others_experiences(self):
        orm_person = ORMPerson.objects.create()
        ORMProfile.objects.create(person_id=orm_person.id, username='a')
        orm_auth_token = ORMAuthToken.objects.create(person=orm_person)
        orm_other_person = ORMPerson.objects.create()
        ORMProfile.objects.create(person_id=orm_other_person.id, username='other', bio='c')
        exp_a = ORMExperience.objects.create(title='Exp a', description='some description', author=orm_other_person)
        exp_b = ORMExperience.objects.create(title='Exp b', description='other description', author=orm_other_person)
        exp_c = ORMExperience.objects.create(title='Exp c', description='third description', author=orm_other_person)
        ExperienceRepo().save_experience(person_id=orm_person.id, experience_id=exp_c.id)

        client = Client()
        auth_headers = {'HTTP_AUTHORIZATION': 'Token {}'.format(orm_auth_token.access_token), }
        response = client.get("{}?username=other&limit=2".format(reverse('experiences')), **auth_headers)

        assert response.status_code == 200
        body = json.loads(response.content)
        assert body == {
                'results': [
                           {
                               'id': str(exp_c.id),
                               'title': 'Exp c',
                               'description': 'third description',
                               'picture': None,
                               'author_profile': {
                                   'username': 'other',
                                   'bio': 'c',
                                   'picture': None,
                                   'is_me': False,
                                },
                               'is_mine': False,
                               'is_saved': True,
                               'saves_count': 1
                           },
                           {
                               'id': str(exp_b.id),
                               'title': 'Exp b',
                               'description': 'other description',
                               'picture': None,
                               'author_profile': {
                                   'username': 'other',
                                   'bio': 'c',
                                   'picture': None,
                                   'is_me': False,
                                },
                               'is_mine': False,
                               'is_saved': False,
                               'saves_count': 0
                           },
                       ],
                'next_url': 'http://testserver/experiences/?username=other&limit=2&offset=2'
            }

        auth_headers = {'HTTP_AUTHORIZATION': 'Token {}'.format(orm_auth_token.access_token), }
        response = client.get(body['next_url'], **auth_headers)
        assert response.status_code == 200
        body = json.loads(response.content)
        assert body == {
                'results': [
                           {
                               'id': str(exp_a.id),
                               'title': 'Exp a',
                               'description': 'some description',
                               'picture': None,
                               'author_profile': {
                                   'username': 'other',
                                   'bio': 'c',
                                   'picture': None,
                                   'is_me': False,
                                },
                               'is_mine': False,
                               'is_saved': False,
                               'saves_count': 0
                           },
                       ],
                'next_url': None
            }

    def test_saved_experiences_returns_only_saved_scenes(self):
        orm_person = ORMPerson.objects.create()
        ORMProfile.objects.create(person_id=orm_person.id, username='a')
        orm_person_b = ORMPerson.objects.create()
        ORMProfile.objects.create(person_id=orm_person_b.id, username='b', bio='bs')
        orm_auth_token = ORMAuthToken.objects.create(person=orm_person)
        exp_a = ORMExperience.objects.create(title='Exp a', description='some description', author=orm_person_b)
        ORMExperience.objects.create(title='Exp b', description='other description', author=orm_person_b)
        ExperienceRepo().save_experience(orm_person.id, exp_a.id)

        client = Client()
        auth_headers = {'HTTP_AUTHORIZATION': 'Token {}'.format(orm_auth_token.access_token), }
        response = client.get("{}?saved=true".format(reverse('experiences')), **auth_headers)

        assert response.status_code == 200
        body = json.loads(response.content)
        assert body == {
                'results': [
                           {
                               'id': str(exp_a.id),
                               'title': 'Exp a',
                               'description': 'some description',
                               'picture': None,
                               'author_profile': {
                                   'username': 'b',
                                   'bio': 'bs',
                                   'picture': None,
                                   'is_me': False,
                                },
                               'is_mine': False,
                               'is_saved': True,
                               'saves_count': 1
                           }
                       ],
                'next_url': None
                }


class CreateExperienceTestCase(TestCase):

    def test_create_experience_creates_and_returns_experience(self):
        orm_person = ORMPerson.objects.create(is_email_confirmed=True)
        orm_auth_token = ORMAuthToken.objects.create(person_id=orm_person.id)
        ORMProfile.objects.create(person_id=orm_person.id, username='usr.nm', bio='My bio')
        auth_headers = {'HTTP_AUTHORIZATION': 'Token {}'.format(orm_auth_token.access_token), }
        client = Client()
        response = client.post(reverse('experiences'),
                               {'title': 'Experience title', 'description': 'Some description'},
                               **auth_headers)

        body = json.loads(response.content)
        created_experience = ORMExperience.objects.get(id=body['id'], title='Experience title',
                                                       description='Some description')
        assert created_experience is not None
        assert body == {
                           'id': str(created_experience.id),
                           'title': 'Experience title',
                           'description': 'Some description',
                           'picture': None,
                           'author_profile': {
                               'username': 'usr.nm',
                               'bio': 'My bio',
                               'picture': None,
                               'is_me': True,
                           },
                           'is_mine': True,
                           'is_saved': False,
                           'saves_count': 0
                       }

    def test_wrong_attributes_doesnt_create_and_returns_error(self):
        orm_person = ORMPerson.objects.create(is_email_confirmed=True)
        orm_auth_token = ORMAuthToken.objects.create(person_id=orm_person.id)
        auth_headers = {'HTTP_AUTHORIZATION': 'Token {}'.format(orm_auth_token.access_token), }
        client = Client()
        response = client.post(reverse('experiences'), {'title': '', 'description': 'Some description'}, **auth_headers)

        assert not ORMExperience.objects.filter(title='', description='Some description').exists()
        body = json.loads(response.content)
        assert body == {
                           'error': {
                                        'source': 'title',
                                        'code': 'wrong_size',
                                        'message': 'Title must be between 1 and 80 chars'
                                    }
                       }


class ModifyExperienceTestCase(TestCase):

    def test_modifies_and_returns_experience(self):
        orm_person = ORMPerson.objects.create()
        orm_auth_token = ORMAuthToken.objects.create(person_id=orm_person.id)
        ORMProfile.objects.create(person_id=orm_person.id, username='usr.nm')
        auth_headers = {'HTTP_AUTHORIZATION': 'Token {}'.format(orm_auth_token.access_token), }
        orm_experience = ORMExperience.objects.create(title='T', description='', author=orm_person)

        client = Client()
        response = client.patch(reverse('experience', args=[orm_experience.id]),
                                urllib.parse.urlencode({"description": "New description"}),
                                **auth_headers,
                                content_type='application/x-www-form-urlencoded')

        body = json.loads(response.content)
        updated_experience = ORMExperience.objects.get(id=orm_experience.id, title='T', description='New description')
        assert updated_experience is not None
        assert body == {
                           'id': str(orm_experience.id),
                           'title': 'T',
                           'description': 'New description',
                           'picture': None,
                           'author_profile': {
                               'username': 'usr.nm',
                               'bio': '',
                               'picture': None,
                               'is_me': True,
                           },
                           'is_mine': True,
                           'is_saved': False,
                           'saves_count': 0
                       }

    def test_wrong_attributes_doesnt_update_and_returns_error(self):
        orm_person = ORMPerson.objects.create()
        orm_auth_token = ORMAuthToken.objects.create(person_id=orm_person.id)
        ORMProfile.objects.create(person_id=orm_person.id, username='a')
        orm_experience = ORMExperience.objects.create(title='T', description='', author=orm_person)

        auth_headers = {'HTTP_AUTHORIZATION': 'Token {}'.format(orm_auth_token.access_token), }
        client = Client()
        response = client.patch(reverse('experience', args=[orm_experience.id]),
                                urllib.parse.urlencode({"title": "", "description": "Some description"}),
                                content_type='application/x-www-form-urlencoded', **auth_headers)

        assert not ORMExperience.objects.filter(title='', description='Some description').exists()
        body = json.loads(response.content)
        assert body == {
                           'error': {
                                        'source': 'title',
                                        'code': 'wrong_size',
                                        'message': 'Title must be between 1 and 80 chars'
                                    }
                       }


class SaveUnsaveExperienceTestCase(TestCase):

    def test_save_post_returns_201_and_creates_save_db_entry(self):
        SaveUnsaveExperienceTestCase.ScenarioMaker() \
                .given_a_person_with_auth_token() \
                .given_an_experience() \
                .when_post_on_experience_save() \
                .then_save_entry_should_be_created_on_db() \
                .then_response_should_be_201()

    def test_save_delete_returns_204_and_removes_save_db_entry(self):
        SaveUnsaveExperienceTestCase.ScenarioMaker() \
                .given_a_person_with_auth_token() \
                .given_an_experience() \
                .given_a_save_for_that_person_and_experience() \
                .when_delete_on_experience_save() \
                .then_save_entry_should_be_removed_from_db() \
                .then_response_should_be_204()

    class ScenarioMaker:

        def given_a_person_with_auth_token(self):
            self.orm_person = ORMPerson.objects.create()
            self.orm_auth_token = ORMAuthToken.objects.create(person_id=self.orm_person.id)
            ORMProfile.objects.create(person_id=self.orm_person.id, username='caller')
            return self

        def given_an_experience(self):
            orm_author = ORMPerson.objects.create()
            ORMProfile.objects.create(person_id=orm_author.id, username='creator')
            self.orm_experience = ORMExperience.objects.create(title='T', description='', author=orm_author)
            return self

        def given_a_save_for_that_person_and_experience(self):
            ORMSave.objects.create(person=self.orm_person, experience=self.orm_experience)
            return self

        def when_post_on_experience_save(self):
            auth_headers = {'HTTP_AUTHORIZATION': 'Token {}'.format(self.orm_auth_token.access_token), }
            client = Client()
            self.response = client.post(reverse('experience-save', args=[self.orm_experience.id]), **auth_headers)
            return self

        def when_delete_on_experience_save(self):
            auth_headers = {'HTTP_AUTHORIZATION': 'Token {}'.format(self.orm_auth_token.access_token), }
            client = Client()
            self.response = client.delete(reverse('experience-save', args=[self.orm_experience.id]), **auth_headers)
            return self

        def then_save_entry_should_be_created_on_db(self):
            assert ORMSave.objects.filter(person=self.orm_person, experience=self.orm_experience).exists()
            return self

        def then_save_entry_should_be_removed_from_db(self):
            assert not ORMSave.objects.filter(person=self.orm_person, experience=self.orm_experience).exists()
            return self

        def then_response_should_be_201(self):
            assert self.response.status_code == 201
            return self

        def then_response_should_be_204(self):
            assert self.response.status_code == 204
            assert len(self.response.content) == 0
            return self


class SearchExperiencesTestCase(TestCase):

    BARCELONA = (41.385064, 2.173403)
    BERLIN = (52.520007, 13.404954)
    CUSCO = (-13.531950, -71.967463)

    def test_search_experiences_returns_them_pagination_and_200(self):
        SearchExperiencesTestCase.ScenarioMaker() \
                .given_a_person_with_auth_token() \
                .given_an_experience(title='bike routes') \
                .given_an_experience(title='mountayn bike routes with typo and lot of text to decrease importance') \
                .given_an_experience(title='mountain best sites', description='mountain') \
                .given_an_experience(title='barcelona restaurants') \
                .given_an_experience(title='romanic monuments') \
                .when_index_everything_and_search(word='mountain', offset=0, limit=1) \
                .then_should_return_experiences_and_next_url(['3'], 'mountain', 1, 1) \
                .when_index_everything_and_search(word='mountain', offset=1, limit=1) \
                .then_should_return_experiences_and_next_url_null(['2'])

    def test_search_with_location(self):
        SearchExperiencesTestCase.ScenarioMaker() \
                .given_a_person_with_auth_token() \
                .given_an_experience(saves_count=1000) \
                .given_an_scene(description='barcelona restaurants',
                                latitude=SearchExperiencesTestCase.BARCELONA[0],
                                longitude=SearchExperiencesTestCase.BARCELONA[1], experience_id_of_number=1) \
                .given_an_experience(saves_count=1000000) \
                .given_an_scene(description='cusco restaurants',
                                latitude=SearchExperiencesTestCase.CUSCO[0],
                                longitude=SearchExperiencesTestCase.CUSCO[1], experience_id_of_number=2) \
                .given_an_experience(saves_count=100000) \
                .given_an_scene(description='berlin restaurants',
                                latitude=SearchExperiencesTestCase.BERLIN[0],
                                longitude=SearchExperiencesTestCase.BERLIN[1], experience_id_of_number=3) \
                .when_index_everything_and_search(word='restaurants',
                                                  latitude=SearchExperiencesTestCase.BARCELONA[0],
                                                  longitude=SearchExperiencesTestCase.BARCELONA[1],
                                                  offset=0, limit=2) \
                .then_should_return_experiences_and_next_url(['1', '3'], 'restaurants', 2, 2,
                                                             latitude=SearchExperiencesTestCase.BARCELONA[0],
                                                             longitude=SearchExperiencesTestCase.BARCELONA[1]) \
                .when_index_everything_and_search(word='restaurants',
                                                  latitude=SearchExperiencesTestCase.BARCELONA[0],
                                                  longitude=SearchExperiencesTestCase.BARCELONA[1],
                                                  offset=2, limit=2) \
                .then_should_return_experiences_and_next_url_null(['2'])

    class ScenarioMaker:

        def __init__(self):
            self.repo = create_experience_elastic_repo()
            try:
                self.repo._delete_experience_index()
            except NotFoundError:
                pass
            self.repo._create_experience_index()
            self.experiences = []
            self.scenes = []

        def given_a_person_with_auth_token(self):
            self.orm_person = ORMPerson.objects.create()
            self.orm_auth_token = ORMAuthToken.objects.create(person_id=self.orm_person.id)
            self.orm_profile = ORMProfile.objects.create(person_id=self.orm_person.id, username='u', bio='b')
            return self

        def given_an_experience(self, title='', description='', saves_count=0):
            experience = Experience(id=str(len(self.experiences)+1), title=title,
                                    description=description, author_id=self.orm_person.id,
                                    author_profile=Profile(person_id=self.orm_person.id, username='u',
                                                           bio='b', picture=None, is_me=True),
                                    saves_count=saves_count, is_mine=True)

            db_experience = ExperienceRepo().create_experience(experience)
            ORMExperience.objects.filter(id=db_experience.id).update(saves_count=saves_count)

            experience = experience.builder().id(db_experience.id).build()
            self.experiences.append(experience)

            return self

        def given_an_scene(self, title='', description='', latitude=0.0, longitude=0.0, experience_id_of_number=1):
            scene = Scene(id=str(len(self.scenes)+1), title=title,
                          description=description, latitude=latitude, longitude=longitude,
                          experience_id=self.experiences[experience_id_of_number-1].id)
            self.scenes.append(scene)
            return self

        def when_index_everything_and_search(self, word, latitude=None, longitude=None, offset=0, limit=20):
            for experience in self.experiences:
                experience_scenes = [scene for scene in self.scenes if scene.experience_id == experience.id]
                self.repo.index_experience_and_its_scenes(experience, experience_scenes)
            self.repo._refresh_experience_index()
            client = Client()
            auth_headers = {'HTTP_AUTHORIZATION': 'Token {}'.format(self.orm_auth_token.access_token), }
            search_url = "{}?offset={}&limit={}&word={}".format(reverse('search-experiences'), offset, limit, word)
            if latitude is not None:
                search_url = "{}&latitude={}".format(search_url, latitude)
            if longitude is not None:
                search_url = "{}&longitude={}".format(search_url, longitude)
            self.response = client.get(search_url, **auth_headers)
            return self

        def then_should_return_experiences_and_next_url_null(self, experiences_ids):
            experiences = [self.experiences[int(i)-1] for i in experiences_ids]
            assert self.response.status_code == 200
            assert json.loads(self.response.content) == {
                    'results': serialize_multiple_experiences(experiences), 'next_url': None}
            return self

        def then_should_return_experiences_and_next_url(self, experiences_ids, word,
                                                        offset, limit, latitude=None, longitude=None):
            experiences = [self.experiences[int(i)-1] for i in experiences_ids]
            next_url = 'http://testserver/experiences/search?offset={}&limit={}&word={}'.format(offset, limit, word)
            if latitude is not None:
                next_url = "{}&latitude={}".format(next_url, latitude)
            if longitude is not None:
                next_url = "{}&longitude={}".format(next_url, longitude)
            assert self.response.status_code == 200
            assert json.loads(self.response.content) == {
                    'results': serialize_multiple_experiences(experiences), 'next_url': next_url}
            return self


class ExperienceShareUrlTestCase(TransactionTestCase):

    def test_experience_already_has_share_id_returns_that(self):
        ExperienceShareUrlTestCase.ScenarioMaker() \
                .given_a_person_with_auth_token() \
                .given_an_experience(share_id='Aib1dR14') \
                .when_get_share_url(1) \
                .then_response_should_be({'share_url': '{}/e/Aib1dR14'.format(settings.PUBLIC_DOMAIN)}, 200)

    def test_experience_without_share_id_creates_it_and_returns(self):
        ExperienceShareUrlTestCase.ScenarioMaker() \
                .given_a_person_with_auth_token() \
                .given_an_experience() \
                .given_an_id_generator_that_returns(['aSe43DwR']) \
                .when_get_share_url(1) \
                .then_response_should_be({'share_url': '{}/e/aSe43DwR'.format(settings.PUBLIC_DOMAIN)}, 200) \
                .then_experiences_should_be_updated_with(['aSe43DwR'])

    def test_after_duplicate_share_id_generates_other_and_returns(self):
        ExperienceShareUrlTestCase.ScenarioMaker() \
                .given_a_person_with_auth_token() \
                .given_an_experience() \
                .given_an_experience() \
                .given_an_id_generator_that_returns(['aSe43DwR', 'aSe43DwR', 'aSe43DwR', 'Ujd8907J']) \
                .when_get_share_url(1) \
                .then_response_should_be({'share_url': '{}/e/aSe43DwR'.format(settings.PUBLIC_DOMAIN)}, 200) \
                .when_get_share_url(2) \
                .then_response_should_be({'share_url': '{}/e/Ujd8907J'.format(settings.PUBLIC_DOMAIN)}, 200) \
                .then_experiences_should_be_updated_with(['aSe43DwR', 'Ujd8907J'])

    class ScenarioMaker:

        def __init__(self):
            self.experiences = []

        def given_a_person_with_auth_token(self):
            self.orm_person = ORMPerson.objects.create()
            self.orm_auth_token = ORMAuthToken.objects.create(person_id=self.orm_person.id)
            self.orm_profile = ORMProfile.objects.create(person_id=self.orm_person.id, username=str(self.orm_person.id))
            return self

        def given_an_experience(self, share_id=None):
            self.experiences.append(ORMExperience.objects.create(author=self.orm_person, share_id=share_id))
            return self

        def given_an_id_generator_that_returns(self, share_ids):
            from experiences import factories
            fake_id_generator = Mock()
            fake_id_generator.generate.side_effect = share_ids
            factories.create_id_generator = Mock()
            factories.create_id_generator.return_value = fake_id_generator
            return self

        def when_get_share_url(self, exp_position):
            client = Client()
            auth_headers = {'HTTP_AUTHORIZATION': 'Token {}'.format(self.orm_auth_token.access_token), }
            self.response = client.get(reverse('experience-share-url', args=[self.experiences[exp_position-1].id]),
                                       **auth_headers)
            return self

        def then_response_should_be(self, body, status):
            assert json.loads(self.response.content) == body
            assert self.response.status_code == status
            return self

        def then_experiences_should_be_updated_with(self, share_ids):
            for experience, share_id in zip(self.experiences, share_ids):
                experience.refresh_from_db()
                assert experience.share_id == share_id
            return self


class TranslateExperienceShareIdTestCase(TestCase):

    def test_returns_experience_id(self):
        TranslateExperienceShareIdTestCase.ScenarioMaker() \
                .given_a_person_with_auth_token() \
                .given_an_experience(share_id='Aib1dR14') \
                .when_translate_share_id('Aib1dR14') \
                .then_response_should_be_experience_id_and_200()

    class ScenarioMaker:

        def given_a_person_with_auth_token(self):
            self.orm_person = ORMPerson.objects.create()
            self.orm_auth_token = ORMAuthToken.objects.create(person_id=self.orm_person.id)
            ORMProfile.objects.create(person_id=self.orm_person.id, username='a')
            return self

        def given_an_experience(self, share_id=None):
            self.experience = ORMExperience.objects.create(author=self.orm_person, share_id=share_id)
            return self

        def when_translate_share_id(self, share_id):
            client = Client()
            auth_headers = {'HTTP_AUTHORIZATION': 'Token {}'.format(self.orm_auth_token.access_token), }
            self.response = client.get(reverse('translate-experience-share-id', args=[share_id]),
                                       **auth_headers)
            return self

        def then_response_should_be_experience_id_and_200(self):
            assert json.loads(self.response.content) == {'experience_id': str(self.experience.id)}
            assert self.response.status_code == 200
            return self


class GetExperienceTestCase(TestCase):

    def test_returns_experience(self):
        GetExperienceTestCase.ScenarioMaker() \
                .given_a_person_with_auth_token() \
                .given_an_experience_in_db() \
                .when_get_is_called_for_experience() \
                .then_response_should_be_experience_and_200()

    def test_block_author_experience_returns_exception_and_403(self):
        GetExperienceTestCase.ScenarioMaker() \
                .given_a_person_with_auth_token() \
                .given_another_person_blocked_by_first() \
                .given_an_experience_in_db_from_second_person() \
                .when_get_is_called_for_experience() \
                .then_response_should_be_403_blocked_content_exception()

    class ScenarioMaker:

        def given_a_person_with_auth_token(self):
            self.orm_person = ORMPerson.objects.create()
            self.orm_auth_token = ORMAuthToken.objects.create(person_id=self.orm_person.id)
            ORMProfile.objects.create(person_id=self.orm_person.id, username='a')
            return self

        def given_another_person_blocked_by_first(self):
            self.second_orm_person = ORMPerson.objects.create()
            ORMProfile.objects.create(person_id=self.second_orm_person.id, username='b')
            ORMBlock.objects.create(creator=self.orm_person, target=self.second_orm_person)
            return self

        def given_an_experience_in_db(self):
            self.experience = ORMExperience.objects.create(author=self.orm_person)
            return self

        def given_an_experience_in_db_from_second_person(self):
            self.experience = ORMExperience.objects.create(author=self.second_orm_person)
            return self

        def when_get_is_called_for_experience(self):
            client = Client()
            auth_headers = {'HTTP_AUTHORIZATION': 'Token {}'.format(self.orm_auth_token.access_token), }
            self.response = client.get(reverse('experience', args=[str(self.experience.id)]), **auth_headers)
            return self

        def then_response_should_be_experience_and_200(self):
            assert json.loads(self.response.content) == {
                        'id': str(self.experience.id),
                        'title': self.experience.title,
                        'description': self.experience.description,
                        'picture': None,
                        'author_profile': {
                            'username': self.experience.author.profile.username,
                            'bio':  self.experience.author.profile.bio,
                            'picture': None,
                            'is_me': True,
                        },
                        'is_mine': True,
                        'is_saved': False,
                        'saves_count': self.experience.saves_count,
                    }
            assert self.response.status_code == 200
            return self

        def then_response_should_be_403_blocked_content_exception(self):
            assert json.loads(self.response.content) == {
                    'error': {
                        'source': 'content',
                        'code': 'blocked',
                        'message': 'Content is blocked'
                    }
                }
            assert self.response.status_code == 403
            return self


class FlagExperienceTestCase(TestCase):

    def test_flag_post_returns_201_and_creates_flag_db_entry(self):
        FlagExperienceTestCase.ScenarioMaker() \
                .given_a_person_with_auth_token() \
                .given_an_experience() \
                .when_post_on_experience_flag(reason='Spam') \
                .then_flag_entry_should_be_created_on_db(reason='Spam') \
                .then_response_should_be_201()

    class ScenarioMaker:

        def given_a_person_with_auth_token(self):
            self.orm_person = ORMPerson.objects.create()
            self.orm_auth_token = ORMAuthToken.objects.create(person_id=self.orm_person.id)
            ORMProfile.objects.create(person_id=self.orm_person.id, username='caller')
            return self

        def given_an_experience(self):
            orm_author = ORMPerson.objects.create()
            ORMProfile.objects.create(person_id=orm_author.id, username='creator')
            self.orm_experience = ORMExperience.objects.create(title='T', description='', author=orm_author)
            return self

        def when_post_on_experience_flag(self, reason):
            auth_headers = {'HTTP_AUTHORIZATION': 'Token {}'.format(self.orm_auth_token.access_token), }
            client = Client()
            self.response = client.post(reverse('experience-flag', args=[self.orm_experience.id]),
                                        {'reason': reason}, **auth_headers)
            return self

        def then_flag_entry_should_be_created_on_db(self, reason):
            assert ORMFlag.objects.filter(person=self.orm_person,
                                          experience=self.orm_experience, reason=reason).exists()
            return self

        def then_response_should_be_201(self):
            assert self.response.status_code == 201
            return self
