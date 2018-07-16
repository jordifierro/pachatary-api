from elasticsearch.exceptions import NotFoundError
from mock import Mock

from django.test import TestCase

from pachatary.exceptions import EntityDoesNotExistException, ConflictException
from experiences.entities import Experience
from experiences.models import ORMExperience, ORMSave
from experiences.repositories import ExperienceRepo
from experiences.factories import create_experience_elastic_repo
from scenes.entities import Scene
from people.models import ORMPerson
from profiles.models import ORMProfile


class ExperienceRepoTestCase(TestCase):

    def test_get_saved_experiences(self):
        ExperienceRepoTestCase.ScenarioMaker() \
                .given_a_person_in_db('me') \
                .given_a_person_in_db('other.user') \
                .given_an_experience_in_db(created_by_person=2) \
                .given_an_experience_in_db(created_by_person=2) \
                .given_an_experience_in_db(created_by_person=2) \
                .given_an_experience_in_db(created_by_person=2) \
                .given_an_experience_in_db(created_by_person=2) \
                .given_an_experience_in_db(created_by_person=2) \
                .given_an_experience_in_db(created_by_person=1) \
                .given_I_save_experience(experience=3) \
                .given_I_save_experience(experience=5) \
                .given_I_save_experience(experience=1) \
                .given_I_save_experience(experience=6) \
                .when_get_saved_experiences(offset=0, limit=2) \
                .then_result_should_be_experiences_and_offset([6, 1], 2) \
                .when_get_saved_experiences(offset=2, limit=1) \
                .then_result_should_be_experiences_and_offset([5], 3) \
                .when_get_saved_experiences(offset=3, limit=3) \
                .then_result_should_be_experiences_and_offset([3], None)

    def test_get_mine_experiences(self):
        ExperienceRepoTestCase.ScenarioMaker() \
                .given_a_person_in_db('me') \
                .given_a_person_in_db('other.user') \
                .given_an_experience_in_db(created_by_person=1) \
                .given_an_experience_in_db(created_by_person=2) \
                .given_an_experience_in_db(created_by_person=1) \
                .given_an_experience_in_db(created_by_person=1) \
                .given_an_experience_in_db(created_by_person=2) \
                .given_an_experience_in_db(created_by_person=1) \
                .given_an_experience_in_db(created_by_person=1) \
                .given_I_save_experience(experience=5) \
                .when_get_person_experiences(target_person=1, offset=0, limit=2) \
                .then_result_should_be_experiences_and_offset([7, 6], 2) \
                .when_get_person_experiences(target_person=1, offset=2, limit=1) \
                .then_result_should_be_experiences_and_offset([4], 3) \
                .when_get_person_experiences(target_person=1, offset=3, limit=3) \
                .then_result_should_be_experiences_and_offset([3, 1], None)

    def test_other_s_experiences(self):
        ExperienceRepoTestCase.ScenarioMaker() \
                .given_a_person_in_db('me') \
                .given_a_person_in_db('other.user') \
                .given_an_experience_in_db(created_by_person=2) \
                .given_an_experience_in_db(created_by_person=2) \
                .given_an_experience_in_db(created_by_person=1) \
                .given_an_experience_in_db(created_by_person=2) \
                .given_an_experience_in_db(created_by_person=2) \
                .given_an_experience_in_db(created_by_person=1) \
                .given_an_experience_in_db(created_by_person=2) \
                .given_I_save_experience(experience=7) \
                .given_I_save_experience(experience=4) \
                .when_get_person_experiences(target_person=2, offset=0, limit=2) \
                .then_result_should_be_experiences_and_offset([7, 5], 2) \
                .when_get_person_experiences(target_person=2, offset=2, limit=1) \
                .then_result_should_be_experiences_and_offset([4], 3) \
                .when_get_person_experiences(target_person=2, offset=3, limit=3) \
                .then_result_should_be_experiences_and_offset([2, 1], None)

    def test_get_mine_experience_returns_experience(self):
        ExperienceRepoTestCase.ScenarioMaker() \
                .given_a_person_in_db('me') \
                .given_an_experience_in_db(created_by_person=1) \
                .when_get_experience(1, person=1) \
                .then_repo_should_return_experience(1, person_logged=1, saved=False)

    def test_get_others_experience_returns_experience(self):
        ExperienceRepoTestCase.ScenarioMaker() \
                .given_a_person_in_db('me') \
                .given_a_person_in_db('other.user') \
                .given_an_experience_in_db(created_by_person=2) \
                .when_get_experience(1, person=1) \
                .then_repo_should_return_experience(1, person_logged=1, saved=False)

    def test_get_saved_experience_returns_experience(self):
        ExperienceRepoTestCase.ScenarioMaker() \
                .given_a_person_in_db('me') \
                .given_a_person_in_db('other.user') \
                .given_an_experience_in_db(created_by_person=2) \
                .given_I_save_experience(experience=1) \
                .when_get_experience(1, person=1) \
                .then_repo_should_return_experience(1, person_logged=1, saved=True)

    def test_get_experience_by_share_id_returns_experience(self):
        ExperienceRepoTestCase.ScenarioMaker() \
                .given_a_person_in_db('me') \
                .given_an_experience_in_db(created_by_person=1, share_id='sdREwe43') \
                .when_get_experience_by_share_id('sdREwe43', person=1) \
                .then_repo_should_return_experience(1, person_logged=1, saved=False)

    def test_get_unexistent_experience_raises_error(self):
        ExperienceRepoTestCase.ScenarioMaker() \
                .when_get_unexistent_experience() \
                .then_entity_does_not_exists_should_be_raised()

    def test_create_experience_creates_and_returns_experience(self):
        ExperienceRepoTestCase.ScenarioMaker() \
                .given_a_person_in_db('me') \
                .when_create_experience(title='e', description='d', author=1) \
                .then_should_return_experience(title='e', description='d', author=1, mine=True) \
                .then_result_experience_should_be_in_db()

    def test_update_experience(self):
        ExperienceRepoTestCase.ScenarioMaker() \
                .given_a_person_in_db('me') \
                .given_an_experience_in_db(created_by_person=1) \
                .when_update_experience(experience=1, title='n', description='u', share_id='Ab3') \
                .then_should_return_experience(title='n', description='u', author=1, mine=True, share_id='Ab3') \
                .then_result_experience_should_be_in_db()

    def test_update_others_experience(self):
        ExperienceRepoTestCase.ScenarioMaker() \
                .given_a_person_in_db('me') \
                .given_a_person_in_db('other') \
                .given_an_experience_in_db(created_by_person=2) \
                .when_update_experience(experience=1, title='', description='', share_id='Ab3') \
                .then_should_return_experience(title='', description='', author=2, mine=False, share_id='Ab3') \
                .then_result_experience_should_be_in_db()

    def test_update_experience_returns_conflict_when_integrity_error(self):
        ExperienceRepoTestCase.ScenarioMaker() \
                .given_a_person_in_db('me') \
                .given_an_experience_in_db(created_by_person=1) \
                .given_an_experience_in_db(created_by_person=1, share_id='Ab3') \
                .when_update_experience(experience=1, title='n', description='u', share_id='Ab3') \
                .then_should_raise_conflict_exception()

    def test_save_experience(self):
        ExperienceRepoTestCase.ScenarioMaker() \
                .given_a_person_in_db('me') \
                .given_a_person_in_db('other') \
                .given_an_experience_in_db(created_by_person=2) \
                .when_save_experience(1) \
                .then_result_should_be_true() \
                .then_save_should_be_in_db(how_many_saves=1, person=1, experience=1) \
                .then_experience_saves_count_should_be(experience=1, saves_count=1)

    def test_save_twice_doesnt_create_2_saves(self):
        ExperienceRepoTestCase.ScenarioMaker() \
                .given_a_person_in_db('me') \
                .given_a_person_in_db('other') \
                .given_an_experience_in_db(created_by_person=2) \
                .given_I_save_experience(experience=1) \
                .when_save_experience(1) \
                .then_result_should_be_true() \
                .then_save_should_be_in_db(how_many_saves=1, person=1, experience=1) \
                .then_experience_saves_count_should_be(experience=1, saves_count=1)

    def test_unsave_experience(self):
        ExperienceRepoTestCase.ScenarioMaker() \
                .given_a_person_in_db('me') \
                .given_a_person_in_db('other') \
                .given_an_experience_in_db(created_by_person=2) \
                .given_I_save_experience(experience=1) \
                .when_unsave_experience(1) \
                .then_result_should_be_true() \
                .then_save_should_be_in_db(how_many_saves=0, person=1, experience=1) \
                .then_experience_saves_count_should_be(experience=1, saves_count=0)

    def test_search_experiences_populates_correcty(self):
        ExperienceRepoTestCase.ScenarioMaker() \
                .given_a_person_in_db('me') \
                .given_a_person_in_db('other') \
                .given_an_experience_in_db(created_by_person=1) \
                .given_an_experience_in_db(created_by_person=2) \
                .given_an_experience_in_db(created_by_person=2) \
                .given_I_save_experience(2) \
                .given_a_word_location_limit_and_offset() \
                .given_a_search_repo_that_returns_experience_ids_and_offset([3, 2, 1], 7) \
                .when_search_experiences() \
                .then_should_call_search_repo_search_experiences_with_correct_params() \
                .then_result_should_be_experiences_and_offset([3, 2, 1], 7)

    def test_search_experiences_populates_keeping_result_order(self):
        ExperienceRepoTestCase.ScenarioMaker() \
                .given_a_person_in_db('me') \
                .given_a_person_in_db('other') \
                .given_an_experience_in_db(created_by_person=1) \
                .given_an_experience_in_db(created_by_person=2) \
                .given_an_experience_in_db(created_by_person=2) \
                .given_I_save_experience(2) \
                .given_a_word_location_limit_and_offset() \
                .given_a_search_repo_that_returns_experience_ids_and_offset([2, 3, 1], 7) \
                .when_search_experiences() \
                .then_should_call_search_repo_search_experiences_with_correct_params() \
                .then_result_should_be_experiences_and_offset([2, 3, 1], 7)

    class ScenarioMaker:

        def __init__(self):
            self.persons = []
            self.profiles = []
            self.experiences = []
            self.saves = []
            self.search_repo = Mock()
            self.repo = ExperienceRepo(self.search_repo)

        def given_a_person_in_db(self, username):
            self.persons.append(ORMPerson.objects.create())
            self.profiles.append(ORMProfile.objects.create(person=self.persons[len(self.persons)-1], username=username))
            return self

        def given_an_experience_in_db(self, created_by_person, share_id=None):
            author_id = self.persons[created_by_person-1].id
            self.experiences.append(ORMExperience.objects.create(author_id=author_id, share_id=share_id))
            return self

        def given_I_save_experience(self, experience):
            experience_id = str(self.experiences[experience-1].id)
            self.repo.save_experience(person_id=str(self.persons[0].id), experience_id=experience_id)
            self.saves.append(experience_id)
            return self

        def given_a_word_location_limit_and_offset(self):
            self.word = 'culture'
            self.location = (5.4, -0.8)
            self.offset = 4
            self.limit = 10
            return self

        def given_a_search_repo_that_returns_experience_ids_and_offset(self, experiences_positions, offset):
            experiences_ids = [self.experiences[i-1].id for i in experiences_positions]
            self.search_repo.search_experiences.return_value = {'results': experiences_ids, 'next_offset': offset}
            return self

        def when_get_saved_experiences(self, offset, limit):
            self.result = self.repo.get_saved_experiences(logged_person_id=str(self.persons[0].id),
                                                          offset=offset, limit=limit)
            return self

        def when_get_person_experiences(self, target_person, offset, limit):
            self.result = self.repo.get_person_experiences(logged_person_id=str(self.persons[0].id),
                                                           target_person_id=str(self.persons[target_person-1].id),
                                                           offset=offset, limit=limit)
            return self

        def when_get_experience(self, position, person=0):
            self.result = self.repo.get_experience(id=str(self.experiences[position-1].id),
                                                   logged_person_id=str(self.persons[person-1].id))
            return self

        def when_get_experience_by_share_id(self, share_id, person=0):
            self.result = self.repo.get_experience(share_id=share_id, logged_person_id=str(self.persons[person-1].id))
            return self

        def when_get_unexistent_experience(self):
            try:
                self.repo.get_experience(id='0')
            except EntityDoesNotExistException as e:
                self.entity_does_not_exist_exception = e
            return self

        def when_create_experience(self, title, description, author):
            orm_author = self.persons[author-1]
            experience = Experience(title=title, description=description, author_id=str(orm_author.id))
            self.result = self.repo.create_experience(experience)
            return self

        def when_update_experience(self, experience, title, description, share_id=None):
            experience = self.repo.get_experience(id=str(self.experiences[experience-1].id),
                                                  logged_person_id=str(self.persons[0].id))
            updated_experience = experience.builder().title(title).description(description).share_id(share_id).build()
            try:
                self.result = self.repo.update_experience(updated_experience, logged_person_id=str(self.persons[0].id))
            except Exception as e:
                self.error = e
            return self

        def when_save_experience(self, position):
            experience = self.experiences[position-1]
            self.result = self.repo.save_experience(person_id=str(self.persons[0].id), experience_id=str(experience.id))
            return self

        def when_unsave_experience(self, position):
            experience = self.experiences[position-1]
            self.result = self.repo.unsave_experience(person_id=str(self.persons[0].id),
                                                      experience_id=str(experience.id))
            return self

        def when_search_experiences(self):
            self.result = self.repo.search_experiences(str(self.persons[0].id), self.word,
                                                       self.location, self.offset, self.limit)
            return self

        def then_result_should_be_experiences_and_offset(self, experiences_positions, next_offset):
            assert self.result['next_offset'] == next_offset
            assert len(self.result['results']) == len(experiences_positions)
            for i in range(len(experiences_positions)):
                orm_experience = self.experiences[experiences_positions[i]-1]
                orm_experience.refresh_from_db()
                saved = str(orm_experience.id) in self.saves
                parsed_experience = self.repo._decode_db_experience(orm_experience,
                                                                    str(self.persons[0].id), is_saved=saved)
                assert self.result['results'][i] == parsed_experience

            return self

        def then_repo_should_return_experience(self, position, person_logged, saved=False):
            orm_experience = self.experiences[position-1]
            parsed_experience = self.repo._decode_db_experience(orm_experience, str(self.persons[person_logged-1].id),
                                                                is_saved=saved)
            if saved:
                parsed_experience = parsed_experience.builder().saves_count(1).build()
            assert self.result == parsed_experience
            return self

        def then_entity_does_not_exists_should_be_raised(self):
            assert self.entity_does_not_exist_exception is not None
            return self

        def then_should_return_experience(self, title, description, author, mine, share_id=None):
            assert self.result.title == title
            assert self.result.description == description
            assert self.result.author_profile.person_id == str(self.profiles[author-1].person_id)
            assert self.result.author_profile.username == self.profiles[author-1].username
            assert self.result.author_profile.bio == self.profiles[author-1].bio
            assert self.result.author_profile.is_me == mine
            assert self.result.is_mine == mine
            assert self.result.share_id == share_id
            return self

        def then_result_experience_should_be_in_db(self):
            orm_experience = ORMExperience.objects.get(id=self.result.id)
            assert str(orm_experience.id) == self.result.id
            assert orm_experience.title == self.result.title
            assert orm_experience.description == self.result.description
            assert str(orm_experience.author.profile.person_id) == self.result.author_profile.person_id
            assert orm_experience.author.profile.username == self.result.author_profile.username
            assert orm_experience.author.profile.bio == self.result.author_profile.bio
            assert orm_experience.share_id == self.result.share_id
            return self

        def then_result_should_be_true(self):
            assert self.result is True
            return self

        def then_save_should_be_in_db(self, how_many_saves, person, experience):
            orm_person = self.persons[person-1]
            orm_experience = self.experiences[experience-1]
            assert len(ORMSave.objects.filter(experience_id=orm_experience.id,
                                              person_id=orm_person.id)) == how_many_saves
            return self

        def then_experience_saves_count_should_be(self, experience, saves_count):
            self.experiences[experience-1].refresh_from_db()
            assert self.experiences[experience-1].saves_count == saves_count
            return self

        def then_should_call_search_repo_search_experiences_with_correct_params(self):
            self.search_repo.search_experiences.assert_called_once_with(self.word, self.location,
                                                                        self.offset, self.limit)
            return self

        def then_should_raise_conflict_exception(self):
            assert type(self.error) == ConflictException
            return self


class ExperienceElasticRepoTestCase(TestCase):

    BARCELONA = (41.385064, 2.173403)
    BERLIN = (52.520007, 13.404954)
    CUSCO = (-13.531950, -71.967463)

    def test_search_by_title(self):
        ExperienceElasticRepoTestCase.ScenarioMaker() \
                .given_an_experience(title='bike routes') \
                .given_an_experience(title='mountain bike') \
                .given_an_experience(title='barcelona restaurants') \
                .given_an_experience(title='romanic monuments') \
                .when_index_everything_and_search(word='mountain') \
                .then_should_return_experiences_and_next_offset(['2'])

    def test_search_by_description(self):
        ExperienceElasticRepoTestCase.ScenarioMaker() \
                .given_an_experience(description='bike routes') \
                .given_an_experience(description='alpinism mountain') \
                .given_an_experience(description='barcelona restaurants') \
                .given_an_experience(description='romanic monuments') \
                .when_index_everything_and_search(word='mountain') \
                .then_should_return_experiences_and_next_offset(['2'])

    def test_search_by_scene_title(self):
        ExperienceElasticRepoTestCase.ScenarioMaker() \
                .given_an_experience() \
                .given_an_scene(title='eco tour', experience_id_of_number=1) \
                .given_an_experience() \
                .given_an_scene(title='science museums', experience_id_of_number=2) \
                .given_an_experience() \
                .given_an_scene(title='ruta del bacalao', experience_id_of_number=3) \
                .when_index_everything_and_search(word='eco') \
                .then_should_return_experiences_and_next_offset(['1'])

    def test_search_by_scene_description(self):
        ExperienceElasticRepoTestCase.ScenarioMaker() \
                .given_an_experience() \
                .given_an_scene(description='eco markets', experience_id_of_number=1) \
                .given_an_experience() \
                .given_an_scene(description='science museums', experience_id_of_number=2) \
                .given_an_experience() \
                .given_an_scene(description='ruta del bacalao', experience_id_of_number=3) \
                .when_index_everything_and_search(word='eco') \
                .then_should_return_experiences_and_next_offset(['1'])

    def test_search_by_title_accepts_typos(self):
        ExperienceElasticRepoTestCase.ScenarioMaker() \
                .given_an_experience(title='bike routes') \
                .given_an_experience(title='mountein bike') \
                .given_an_experience(title='barcelona restaurants') \
                .given_an_experience(title='romanic monuments') \
                .when_index_everything_and_search(word='mountain') \
                .then_should_return_experiences_and_next_offset(['2'])

    def test_search_by_description_accepts_typos(self):
        ExperienceElasticRepoTestCase.ScenarioMaker() \
                .given_an_experience(description='bike routes') \
                .given_an_experience(description='alpinism mountains') \
                .given_an_experience(description='barcelona restaurants') \
                .given_an_experience(description='romanic monuments') \
                .when_index_everything_and_search(word='mountain') \
                .then_should_return_experiences_and_next_offset(['2'])

    def test_search_by_scene_title_accepts_typos(self):
        ExperienceElasticRepoTestCase.ScenarioMaker() \
                .given_an_experience() \
                .given_an_scene(title='eko tour', experience_id_of_number=1) \
                .given_an_experience() \
                .given_an_scene(title='science museums', experience_id_of_number=2) \
                .given_an_experience() \
                .given_an_scene(title='ruta del bacalao', experience_id_of_number=3) \
                .when_index_everything_and_search(word='eco') \
                .then_should_return_experiences_and_next_offset(['1'])

    def test_search_by_scene_description_accepts_typos(self):
        ExperienceElasticRepoTestCase.ScenarioMaker() \
                .given_an_experience() \
                .given_an_scene(description='ecoo markets', experience_id_of_number=1) \
                .given_an_experience() \
                .given_an_scene(description='science museums', experience_id_of_number=2) \
                .given_an_experience() \
                .given_an_scene(description='ruta del bacalao', experience_id_of_number=3) \
                .when_index_everything_and_search(word='eco') \
                .then_should_return_experiences_and_next_offset(['1'])

    def test_search_by_title_sorts_by_length(self):
        ExperienceElasticRepoTestCase.ScenarioMaker() \
                .given_an_experience(title='bike routes') \
                .given_an_experience(title='mountain bike routes for everyone') \
                .given_an_experience(title='mountain') \
                .given_an_experience(title='barcelona restaurants') \
                .given_an_experience(title='romanic monuments') \
                .when_index_everything_and_search(word='mountain') \
                .then_should_return_experiences_and_next_offset(['3', '2'])

    def test_search_by_description_sorts_by_length(self):
        ExperienceElasticRepoTestCase.ScenarioMaker() \
                .given_an_experience(description='mountain bike routes') \
                .given_an_experience(description='bike routes') \
                .given_an_experience(description='alpinism mountain') \
                .given_an_experience(description='barcelona restaurants') \
                .given_an_experience(description='romanic monuments') \
                .when_index_everything_and_search(word='mountain') \
                .then_should_return_experiences_and_next_offset(['3', '1'])

    def test_search_by_scene_title_sorts_by_length(self):
        ExperienceElasticRepoTestCase.ScenarioMaker() \
                .given_an_experience() \
                .given_an_scene(title='eco tour', experience_id_of_number=1) \
                .given_an_experience() \
                .given_an_scene(title='eco markets in your town', experience_id_of_number=2) \
                .given_an_experience() \
                .given_an_scene(title='science museums', experience_id_of_number=3) \
                .given_an_experience() \
                .given_an_scene(title='ruta del bacalao', experience_id_of_number=4) \
                .when_index_everything_and_search(word='eco') \
                .then_should_return_experiences_and_next_offset(['1', '2'])

    def test_search_by_scene_description_sorts_by_length(self):
        ExperienceElasticRepoTestCase.ScenarioMaker() \
                .given_an_experience() \
                .given_an_scene(description='eco markets in your town', experience_id_of_number=1) \
                .given_an_experience() \
                .given_an_scene(description='science museums', experience_id_of_number=2) \
                .given_an_experience() \
                .given_an_scene(description='correbars', experience_id_of_number=3) \
                .given_an_experience() \
                .given_an_scene(description='eco tour', experience_id_of_number=4) \
                .when_index_everything_and_search(word='eco') \
                .then_should_return_experiences_and_next_offset(['4', '1'])

    def test_search_boosts_by_saves_count(self):
        ExperienceElasticRepoTestCase.ScenarioMaker() \
                .given_an_experience(title='bike shopping center', saves_count=1000) \
                .given_an_experience(title='bike tour', saves_count=100) \
                .given_an_experience(title='bike route', saves_count=10000) \
                .when_index_everything_and_search(word='bike') \
                .then_should_return_experiences_and_next_offset(['3', '1', '2'])

    def test_search_boosts_by_location_proximity(self):
        ExperienceElasticRepoTestCase.ScenarioMaker() \
                .given_an_experience() \
                .given_an_scene(description='eco tour', latitude=ExperienceElasticRepoTestCase.BARCELONA[0],
                                longitude=ExperienceElasticRepoTestCase.BARCELONA[1], experience_id_of_number=1) \
                .given_an_experience() \
                .given_an_scene(description='eco markets', latitude=ExperienceElasticRepoTestCase.CUSCO[0],
                                longitude=ExperienceElasticRepoTestCase.CUSCO[1], experience_id_of_number=2) \
                .given_an_experience() \
                .given_an_scene(description='eco shops', latitude=ExperienceElasticRepoTestCase.BERLIN[0],
                                longitude=ExperienceElasticRepoTestCase.BERLIN[1], experience_id_of_number=3) \
                .when_index_everything_and_search(word='eco', location=ExperienceElasticRepoTestCase.BARCELONA) \
                .then_should_return_experiences_and_next_offset(['1', '3', '2'])

    def test_search_location_boost_is_more_important_than_saves(self):
        ExperienceElasticRepoTestCase.ScenarioMaker() \
                .given_an_experience(saves_count=1000) \
                .given_an_scene(description='barcelona restaurants',
                                latitude=ExperienceElasticRepoTestCase.BARCELONA[0],
                                longitude=ExperienceElasticRepoTestCase.BARCELONA[1], experience_id_of_number=1) \
                .given_an_experience(saves_count=1000000) \
                .given_an_scene(description='cusco restaurants',
                                latitude=ExperienceElasticRepoTestCase.CUSCO[0],
                                longitude=ExperienceElasticRepoTestCase.CUSCO[1], experience_id_of_number=2) \
                .given_an_experience(saves_count=100000) \
                .given_an_scene(description='berlin restaurants',
                                latitude=ExperienceElasticRepoTestCase.BERLIN[0],
                                longitude=ExperienceElasticRepoTestCase.BERLIN[1], experience_id_of_number=3) \
                .when_index_everything_and_search(word='restaurants',
                                                  location=ExperienceElasticRepoTestCase.BARCELONA) \
                .then_should_return_experiences_and_next_offset(['1', '3', '2'])

    def test_search_pagination(self):
        ExperienceElasticRepoTestCase.ScenarioMaker() \
                .given_an_experience(title='bike routes') \
                .given_an_experience(title='mountain bike routes for everyone') \
                .given_an_experience(title='mountain') \
                .given_an_experience(title='barcelona restaurants') \
                .given_an_experience(title='romanic monuments') \
                .when_index_everything_and_search(word='mountain', offset=0, limit=1) \
                .then_should_return_experiences_and_next_offset(['3'], 1) \
                .when_index_everything_and_search(word='mountain', offset=1, limit=1) \
                .then_should_return_experiences_and_next_offset(['2'], None)

    def test_search_without_word_boosts_by_saves_count(self):
        ExperienceElasticRepoTestCase.ScenarioMaker() \
                .given_an_experience(title='shopping center', saves_count=1000) \
                .given_an_experience(title='bike tour', saves_count=100) \
                .given_an_experience(title='eco route', saves_count=10000) \
                .when_index_everything_and_search() \
                .then_should_return_experiences_and_next_offset(['3', '1', '2'])

    def test_search_without_word_boosts_by_location_proximity(self):
        ExperienceElasticRepoTestCase.ScenarioMaker() \
                .given_an_experience() \
                .given_an_scene(description='eco tour', latitude=ExperienceElasticRepoTestCase.BARCELONA[0],
                                longitude=ExperienceElasticRepoTestCase.BARCELONA[1], experience_id_of_number=1) \
                .given_an_experience() \
                .given_an_scene(description='local markets', latitude=ExperienceElasticRepoTestCase.CUSCO[0],
                                longitude=ExperienceElasticRepoTestCase.CUSCO[1], experience_id_of_number=2) \
                .given_an_experience() \
                .given_an_scene(description='culture shops', latitude=ExperienceElasticRepoTestCase.BERLIN[0],
                                longitude=ExperienceElasticRepoTestCase.BERLIN[1], experience_id_of_number=3) \
                .when_index_everything_and_search(location=ExperienceElasticRepoTestCase.BARCELONA) \
                .then_should_return_experiences_and_next_offset(['1', '3', '2'])

    def test_search_without_word_location_boost_is_more_important_than_saves(self):
        ExperienceElasticRepoTestCase.ScenarioMaker() \
                .given_an_experience(saves_count=1000) \
                .given_an_scene(description='barcelona monuments',
                                latitude=ExperienceElasticRepoTestCase.BARCELONA[0],
                                longitude=ExperienceElasticRepoTestCase.BARCELONA[1], experience_id_of_number=1) \
                .given_an_experience(saves_count=1000000) \
                .given_an_scene(description='cusco ruins',
                                latitude=ExperienceElasticRepoTestCase.CUSCO[0],
                                longitude=ExperienceElasticRepoTestCase.CUSCO[1], experience_id_of_number=2) \
                .given_an_experience(saves_count=100000) \
                .given_an_scene(description='berlin culture',
                                latitude=ExperienceElasticRepoTestCase.BERLIN[0],
                                longitude=ExperienceElasticRepoTestCase.BERLIN[1], experience_id_of_number=3) \
                .when_index_everything_and_search(location=ExperienceElasticRepoTestCase.BARCELONA) \
                .then_should_return_experiences_and_next_offset(['1', '3', '2'])

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

        def given_an_experience(self, title='', description='', saves_count=0):
            experience = Experience(id=str(len(self.experiences)+1), title=title,
                                    description=description, author_id='0', saves_count=saves_count)
            self.experiences.append(experience)
            return self

        def given_an_scene(self, title='', description='', latitude=0.0, longitude=0.0, experience_id_of_number=1):
            scene = Scene(id=str(len(self.scenes)+1), title=title,
                          description=description, latitude=latitude, longitude=longitude,
                          experience_id=self.experiences[experience_id_of_number-1].id)
            self.scenes.append(scene)
            return self

        def when_index_everything_and_search(self, word=None, location=None, offset=0, limit=20):
            for experience in self.experiences:
                experience_scenes = [scene for scene in self.scenes if scene.experience_id == experience.id]
                self.repo.index_experience_and_its_scenes(experience, experience_scenes)
            self.repo._refresh_experience_index()
            self.result = self.repo.search_experiences(word=word, location=location, offset=offset, limit=limit)
            return self

        def then_should_return_experiences_and_next_offset(self, experience_ids, next_offset=None):
            assert self.result['results'] == experience_ids
            assert self.result['next_offset'] == next_offset
            return self
