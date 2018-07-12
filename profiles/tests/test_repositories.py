from django.test import TestCase

from pachatary.exceptions import EntityDoesNotExistException
from people.repositories import PersonRepo
from profiles.models import ORMProfile
from profiles.repositories import ProfileRepo
from profiles.entities import Profile


class ProfileRepoTestCase(TestCase):

    def test_create_profile(self):
        ProfileRepoTestCase._ScenarioMaker() \
                .given_a_person() \
                .when_create_profile(person=1, username='u', bio='b') \
                .then_result_should_be_profile(person=1, username='u', bio='b') \
                .then_that_profile_should_be_saved_in_db(person=1, username='u', bio='b')

    def test_update_profile(self):
        ProfileRepoTestCase._ScenarioMaker() \
                .given_a_person() \
                .when_create_profile(person=1, username='u', bio='b') \
                .when_update_profile(person=1, username='t', bio='o') \
                .then_result_should_be_profile(person=1, username='t', bio='o') \
                .then_that_profile_should_be_saved_in_db(person=1, username='t', bio='o')

    def test_get_profile_by_person_id(self):
        ProfileRepoTestCase._ScenarioMaker() \
                .given_a_person() \
                .given_a_profile(person=1, username='u', bio='b') \
                .when_get_profile_from_person_id(person=1) \
                .then_result_should_be_profile(person=1, username='u', bio='b')

    def test_get_profile_by_username(self):
        ProfileRepoTestCase._ScenarioMaker() \
                .given_a_person() \
                .given_a_profile(person=1, username='u', bio='b') \
                .when_get_profile_from_username(username='u') \
                .then_result_should_be_profile(person=1, username='u', bio='b')

    def test_get_unexistent_profile_raises_entity_does_not_exist_exception(self):
        ProfileRepoTestCase._ScenarioMaker() \
                .when_get_profile_from_username(username='none') \
                .then_result_should_raise_entity_does_not_exist()

    class _ScenarioMaker:

        def __init__(self):
            self.persons = []
            self.repo = ProfileRepo()

        def given_a_person(self):
            self.persons.append(PersonRepo().create_guest_person())
            return self

        def given_a_profile(self, person, username, bio):
            profile = Profile(person_id=self.persons[person-1].id, username=username, bio=bio)
            self.repo.create_profile(profile)
            return self

        def when_create_profile(self, person, username, bio):
            profile = Profile(person_id=self.persons[person-1].id, username=username, bio=bio)
            self.result = self.repo.create_profile(profile)
            return self

        def when_update_profile(self, person, username, bio):
            profile = Profile(person_id=self.persons[person-1].id, username=username, bio=bio)
            self.result = self.repo.update_profile(profile)
            return self

        def when_get_profile_from_person_id(self, person):
            self.result = self.repo.get_profile(person_id=self.persons[person-1].id)
            return self

        def when_get_profile_from_username(self, username):
            try:
                self.result = self.repo.get_profile(username=username)
            except Exception as e:
                self.error = e
            return self

        def then_result_should_be_profile(self, person, username, bio):
            assert self.result == Profile(person_id=self.persons[person-1].id, username=username, bio=bio)
            return self

        def then_that_profile_should_be_saved_in_db(self, person, username, bio):
            db_profile = ORMProfile.objects.get(person_id=self.persons[person-1].id)
            assert db_profile.username == username
            assert db_profile.bio == bio
            return self

        def then_result_should_raise_entity_does_not_exist(self):
            assert type(self.error) is EntityDoesNotExistException
            return self
