from django.test import TestCase

from pachatary.exceptions import EntityDoesNotExistException
from experiences.entities import Experience
from experiences.models import ORMExperience, ORMSave
from experiences.repositories import ExperienceRepo
from experiences.factories import create_experience_elastic_repo
from scenes.entities import Scene
from people.models import ORMPerson


class ExperienceRepoTestCase(TestCase):

    def test_get_all_experiences_with_mine_false_returns_not_mine_nor_saved_experiences(self):
        ExperienceRepoTestCase.ScenarioMaker() \
                .given_a_person_in_db() \
                .given_an_experience_created_by_first_person_in_db() \
                .given_another_experience_created_by_first_person_in_db() \
                .given_another_person_in_db() \
                .given_an_experience_created_by_second_person_in_db() \
                .given_another_experience_created_by_second_person_in_db() \
                .given_a_third_experience_created_by_second_person_and_saved_by_first() \
                .given_a_fourth_experience_created_by_second_person_and_saved_by_second() \
                .given_logged_person_id_is_first_person_id() \
                .when_get_all_experiences(mine=False) \
                .then_repo_should_return_second_two_experience_and_fourth_with_saved_mine_false_ordered_asc_by_create()

    def test_get_all_experiences_with_mine_true_returns_mine_experiences(self):
        ExperienceRepoTestCase.ScenarioMaker() \
                .given_a_person_in_db() \
                .given_an_experience_created_by_first_person_in_db() \
                .given_another_experience_created_by_first_person_in_db() \
                .given_another_person_in_db() \
                .given_an_experience_created_by_second_person_in_db() \
                .given_another_experience_created_by_second_person_in_db() \
                .given_logged_person_id_is_first_person_id() \
                .when_get_all_experiences(mine=True) \
                .then_repo_should_return_just_first_two_experience_with_mine_true_ordered_asc_by_create()

    def test_get_all_experiences_with_saved_true_returns_only_saved_experiences(self):
        ExperienceRepoTestCase.ScenarioMaker() \
                .given_a_person_in_db() \
                .given_an_experience_created_by_first_person_in_db() \
                .given_another_experience_created_by_first_person_in_db() \
                .given_another_person_in_db() \
                .given_an_experience_created_by_second_person_in_db() \
                .given_another_experience_created_by_second_person_in_db() \
                .given_a_third_experience_created_by_second_person_in_db() \
                .given_a_save_to_third_second_person_experience_from_first_person() \
                .given_a_save_to_first_second_person_experience_from_first_person() \
                .given_logged_person_id_is_first_person_id() \
                .when_get_all_experiences(saved=True) \
                .then_repo_should_return_second_person_experience_with_saved_true_ordered_asc_by_saved()

    def test_get_all_experiences_with_no_experiences_returns_empty(self):
        ExperienceRepoTestCase.ScenarioMaker() \
                .given_a_person_in_db() \
                .given_some_experiences_created_by_that_person(how_many=0) \
                .given_logged_person_id_is_first_person_id() \
                .when_get_all_experiences(mine=True, offset=0, limit=2) \
                .then_repo_should_return_no_experiences_nor_next_offset()

    def test_get_all_experiences_with_less_experiences_than_limit_returns_results_but_no_next_offset(self):
        ExperienceRepoTestCase.ScenarioMaker() \
                .given_a_person_in_db() \
                .given_some_experiences_created_by_that_person(how_many=1) \
                .given_logged_person_id_is_first_person_id() \
                .when_get_all_experiences(mine=True, offset=0, limit=2) \
                .then_repo_should_return_that_experiences_but_not_next_offset()

    def test_get_all_experiences_with_same_limit_and_experiences_returns_results_but_no_next_offset(self):
        ExperienceRepoTestCase.ScenarioMaker() \
                .given_a_person_in_db() \
                .given_some_experiences_created_by_that_person(how_many=2) \
                .given_logged_person_id_is_first_person_id() \
                .when_get_all_experiences(mine=True, offset=0, limit=2) \
                .then_repo_should_return_that_experiences_but_not_next_offset()

    def test_get_all_experiences_with_more_experiences_than_limit_returns_results_and_next_offset(self):
        ExperienceRepoTestCase.ScenarioMaker() \
                .given_a_person_in_db() \
                .given_some_experiences_created_by_that_person(how_many=3) \
                .given_logged_person_id_is_first_person_id() \
                .when_get_all_experiences(mine=True, offset=0, limit=2) \
                .then_repo_should_return_two_experiences_and_next_offset_2()

    def test_get_all_experiences_with_offset_returns_correct_range(self):
        ExperienceRepoTestCase.ScenarioMaker() \
                .given_a_person_in_db() \
                .given_some_experiences_created_by_that_person(how_many=5) \
                .given_logged_person_id_is_first_person_id() \
                .when_get_all_experiences(mine=True, offset=2, limit=2) \
                .then_repo_should_return_third_and_fourth_experiences_and_offset_4()

    def test_get_experience_returns_experience(self):
        ExperienceRepoTestCase.ScenarioMaker() \
                .given_a_person_in_db() \
                .given_an_experience_in_db() \
                .when_get_experience_with_its_id() \
                .then_repo_should_return_experience()

    def test_get_unexistent_experience_raises_error(self):
        ExperienceRepoTestCase.ScenarioMaker() \
                .when_get_unexistent_experience() \
                .then_entity_does_not_exists_should_be_raised()

    def test_create_experience_creates_and_returns_experience(self):
        ExperienceRepoTestCase.ScenarioMaker() \
                .given_a_person_in_db() \
                .given_an_experience_to_create() \
                .when_create_this_experience() \
                .then_should_return_this_experience_with_mine_true() \
                .then_should_save_this_experience_to_db()

    def test_update_experience(self):
        ExperienceRepoTestCase.ScenarioMaker() \
                .given_a_person_in_db() \
                .given_an_experience_in_db() \
                .given_an_updated_experience() \
                .when_update_first_experience() \
                .then_result_should_be_same_as_updated() \
                .then_updated_experience_should_be_saved_on_db()

    def test_save_experience(self):
        ExperienceRepoTestCase.ScenarioMaker() \
                .given_a_person_in_db() \
                .given_an_experience_in_db() \
                .when_save_that_experience() \
                .then_result_should_be_true() \
                .then_save_should_be_created_for_that_experience_and_person() \
                .then_experience_saves_count_should_be(1)

    def test_save_twice_doesnt_create_2_saves(self):
        ExperienceRepoTestCase.ScenarioMaker() \
                .given_a_person_in_db() \
                .given_an_experience_in_db() \
                .given_a_save_for_that_person_and_experience() \
                .when_save_that_experience() \
                .then_result_should_be_true() \
                .then_save_for_that_experience_and_person_should_be_only_one() \
                .then_experience_saves_count_should_be(1)

    def test_unsave_experience(self):
        ExperienceRepoTestCase.ScenarioMaker() \
                .given_a_person_in_db() \
                .given_an_experience_in_db() \
                .given_a_save_for_that_person_and_experience() \
                .when_unsave_that_experience() \
                .then_result_should_be_true() \
                .then_save_should_be_deleted_from_db() \
                .then_experience_saves_count_should_be(0)

    class ScenarioMaker:

        def __init__(self):
            self.orm_person = None
            self.orm_experience_a = None
            self.orm_experience_b = None
            self.experience_a = None
            self.experience_b = None
            self.result = None
            self.entity_does_not_exist_error = None
            self.experience_to_create = None

        def given_a_person_in_db(self):
            self.orm_person = ORMPerson.objects.create(username='usr')
            return self

        def given_another_person_in_db(self):
            self.second_orm_person = ORMPerson.objects.create(username='nme')
            return self

        def given_some_experiences_created_by_that_person(self, how_many):
            self.orm_experiences = []
            self.experiences = []
            for i in range(0, how_many):
                self.orm_experiences.append(ORMExperience.objects.create(title='Exp {}'.format(str(i)),
                                                                         description='dsc',
                                                                         author=self.orm_person))
                self.experiences.append(Experience(id=self.orm_experiences[i].id, title='Exp {}'.format(str(i)),
                                                   description='dsc', author_id=self.orm_person.id, is_mine=True,
                                                   author_username=self.orm_person.username))
            return self

        def given_an_experience_created_by_first_person_in_db(self):
            self.orm_experience_a = ORMExperience.objects.create(title='Exp a', description='some description',
                                                                 author=self.orm_person)
            self.experience_a = Experience(id=self.orm_experience_a.id, title='Exp a', description='some description',
                                           author_id=self.orm_person.id, author_username=self.orm_person.username)
            return self

        def given_another_experience_created_by_first_person_in_db(self):
            self.orm_experience_b = ORMExperience.objects.create(title='Exp b', description='some description',
                                                                 author=self.orm_person)
            self.experience_b = Experience(id=self.orm_experience_b.id, title='Exp b', description='some description',
                                           author_id=self.orm_person.id, author_username=self.orm_person.username)
            return self

        def given_an_experience_created_by_second_person_in_db(self):
            self.orm_experience_c = ORMExperience.objects.create(title='Exp c', description='description',
                                                                 author=self.second_orm_person)
            self.experience_c = Experience(id=self.orm_experience_c.id, title='Exp c', description='description',
                                           author_id=self.second_orm_person.id,
                                           author_username=self.second_orm_person.username)
            return self

        def given_another_experience_created_by_second_person_in_db(self):
            self.orm_experience_d = ORMExperience.objects.create(title='Exp d', description='description',
                                                                 author=self.second_orm_person)
            self.experience_d = Experience(id=self.orm_experience_d.id, title='Exp d', description='description',
                                           author_id=self.second_orm_person.id,
                                           author_username=self.second_orm_person.username)
            return self

        def given_a_third_experience_created_by_second_person_in_db(self):
            self.orm_experience_e = ORMExperience.objects.create(title='Exp e', description='description',
                                                                 author=self.second_orm_person)
            self.experience_e = Experience(id=self.orm_experience_e.id, title='Exp e', description='description',
                                           author_id=self.second_orm_person.id,
                                           author_username=self.second_orm_person.username)
            return self

        def given_a_third_experience_created_by_second_person_and_saved_by_first(self):
            self.orm_experience_e = ORMExperience.objects.create(title='Exp e', description='description',
                                                                 author=self.second_orm_person)
            self.experience_e = Experience(id=self.orm_experience_e.id, title='Exp e', description='description',
                                           author_id=self.second_orm_person.id,
                                           author_username=self.second_orm_person.username)
            ORMSave.objects.create(person=self.orm_person, experience=self.orm_experience_e)
            return self

        def given_a_fourth_experience_created_by_second_person_and_saved_by_second(self):
            self.orm_experience_f = ORMExperience.objects.create(title='Exp f', description='description',
                                                                 author=self.second_orm_person)
            self.experience_f = Experience(id=self.orm_experience_f.id, title='Exp f', description='description',
                                           author_id=self.second_orm_person.id,
                                           author_username=self.second_orm_person.username)
            ExperienceRepo().save_experience(self.second_orm_person.id, self.orm_experience_f.id)
            return self

        def given_logged_person_id_is_first_person_id(self):
            self.logged_person_id = self.orm_person.id
            return self

        def given_an_experience_to_create(self):
            self.experience_to_create = Experience(id="", title='Exp a', description='some description',
                                                   author_id=self.orm_person.id)
            return self

        def given_an_experience_in_db(self):
            self.orm_experience_a = ORMExperience.objects.create(title='Exp a', description='some description',
                                                                 author=self.orm_person)
            self.experience_a = Experience(id=self.orm_experience_a.id, title='Exp a', description='some description',
                                           author_id=self.orm_person.id, author_username=self.orm_person.username)
            return self

        def given_an_updated_experience(self):
            self.updated_experience = Experience(id=self.experience_a.id, title='T2', description='updated',
                                                 author_id=self.orm_person.id,
                                                 author_username=self.orm_person.username)
            return self

        def given_another_experience_in_db(self):
            self.orm_experience_b = ORMExperience.objects.create(title='Exp b', description='other description',
                                                                 author=self.orm_person)
            self.experience_b = Experience(id=self.orm_experience_b.id, title='Exp b',
                                           description='other description',
                                           author_id=self.orm_person.id, author_username=self.orm_person.username)
            return self

        def given_a_save_for_that_person_and_experience(self):
            ExperienceRepo().save_experience(self.orm_person.id, self.orm_experience_a.id)
            return self

        def given_a_save_to_first_second_person_experience_from_first_person(self):
            ExperienceRepo().save_experience(self.orm_person.id, self.orm_experience_c.id)
            return self

        def given_a_save_to_third_second_person_experience_from_first_person(self):
            ExperienceRepo().save_experience(self.orm_person.id, self.orm_experience_e.id)
            return self

        def when_get_all_experiences(self, mine=False, saved=False, offset=0, limit=100):
            self.result = ExperienceRepo().get_all_experiences(self.logged_person_id, offset, limit,
                                                               mine=mine, saved=saved)
            return self

        def when_get_experience_with_its_id(self):
            self.result = ExperienceRepo().get_experience(self.orm_experience_a.id)
            return self

        def when_get_unexistent_experience(self):
            try:
                ExperienceRepo().get_experience(0)
            except EntityDoesNotExistException as e:
                self.entity_does_not_exist_error = e
            return self

        def when_create_this_experience(self):
            self.result = ExperienceRepo().create_experience(self.experience_to_create)
            return self

        def when_update_first_experience(self):
            self.result = ExperienceRepo().update_experience(self.updated_experience)
            return self

        def when_save_that_experience(self):
            try:
                self.result = ExperienceRepo().save_experience(person_id=self.orm_person.id,
                                                               experience_id=self.orm_experience_a.id)
            except Exception as e:
                self.error = e
            return self

        def when_unsave_that_experience(self):
            try:
                self.result = ExperienceRepo().unsave_experience(person_id=self.orm_person.id,
                                                                 experience_id=self.orm_experience_a.id)
            except Exception as e:
                self.error = e
            return self

        def then_repo_should_return_just_first_two_experience_with_mine_true_ordered_asc_by_create(self):
            assert self.result["results"] == [self.experience_b.builder().is_mine(True).build(),
                                              self.experience_a.builder().is_mine(True).build()]
            return self

        def then_repo_should_return_second_two_experience_and_fourth_with_saved_mine_false_ordered_asc_by_create(self):
            assert self.result["results"] == [self.experience_f.builder().saves_count(1).build(),
                                              self.experience_d, self.experience_c]
            return self

        def then_repo_should_return_just_second_two_experience(self):
            assert self.result["results"] == [self.experience_c, self.experience_d]
            return self

        def then_repo_should_return_second_person_experience_with_saved_true_ordered_asc_by_saved(self):
            assert self.result["results"] == [self.experience_c.builder().is_saved(True).saves_count(1).build(),
                                              self.experience_e.builder().is_saved(True).saves_count(1).build()]
            return self

        def then_repo_should_return_experience(self):
            assert self.result == self.experience_a
            return self

        def then_entity_does_not_exists_should_be_raised(self):
            assert self.entity_does_not_exist_error is not None
            return self

        def then_should_return_this_experience_with_mine_true(self):
            assert self.result.title == self.experience_to_create.title
            assert self.result.description == self.experience_to_create.description
            assert self.result.is_mine is True
            return self

        def then_repo_should_return_no_experiences_nor_next_offset(self):
            assert self.result["results"] == []
            assert self.result["next_offset"] is None
            return self

        def then_repo_should_return_that_experiences_but_not_next_offset(self):
            assert self.result["results"] == list(reversed(self.experiences))
            assert self.result["next_offset"] is None
            return self

        def then_repo_should_return_two_experiences_and_next_offset_2(self):
            assert self.result["results"] == list(reversed(self.experiences))[0:2]
            assert self.result["next_offset"] == 2
            return self

        def then_repo_should_return_third_and_fourth_experiences_and_offset_4(self):
            assert self.result["results"] == list(reversed(self.experiences))[2:4]
            assert self.result["next_offset"] == 4
            return self

        def then_should_save_this_experience_to_db(self):
            exp = ExperienceRepo().get_experience(self.result.id)
            assert exp.title == self.experience_to_create.title
            assert exp.description == self.experience_to_create.description
            return self

        def then_result_should_be_same_as_updated(self):
            assert self.updated_experience.title == self.result.title
            assert self.updated_experience.description == self.result.description
            assert not self.result.picture
            return self

        def then_updated_experience_should_be_saved_on_db(self):
            orm_experience = ORMExperience.objects.get(id=self.result.id,
                                                       title=self.updated_experience.title,
                                                       description=self.updated_experience.description)
            assert orm_experience is not None
            return self

        def then_result_should_be_true(self):
            assert self.result is True
            return self

        def then_save_should_be_created_for_that_experience_and_person(self):
            assert ORMSave.objects.filter(person=self.orm_person, experience=self.orm_experience_a).exists()
            return self

        def then_save_for_that_experience_and_person_should_be_only_one(self):
            assert len(ORMSave.objects.filter(person=self.orm_person, experience=self.orm_experience_a)) == 1
            return self

        def then_save_should_be_deleted_from_db(self):
            assert not ORMSave.objects.filter(person=self.orm_person, experience=self.orm_experience_a).exists()
            return self

        def then_experience_saves_count_should_be(self, saves_count):
            self.orm_experience_a.refresh_from_db()
            assert self.orm_experience_a.saves_count == saves_count


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
                .then_should_return_experiences(['2'])

    def test_search_by_description(self):
        ExperienceElasticRepoTestCase.ScenarioMaker() \
                .given_an_experience(description='bike routes') \
                .given_an_experience(description='alpinism mountain') \
                .given_an_experience(description='barcelona restaurants') \
                .given_an_experience(description='romanic monuments') \
                .when_index_everything_and_search(word='mountain') \
                .then_should_return_experiences(['2'])

    def test_search_by_scene_title(self):
        ExperienceElasticRepoTestCase.ScenarioMaker() \
                .given_an_experience() \
                .given_an_scene(title='eco tour', experience_id_of_number=1) \
                .given_an_experience() \
                .given_an_scene(title='science museums', experience_id_of_number=2) \
                .given_an_experience() \
                .given_an_scene(title='ruta del bacalao', experience_id_of_number=3) \
                .when_index_everything_and_search(word='eco') \
                .then_should_return_experiences(['1'])

    def test_search_by_scene_description(self):
        ExperienceElasticRepoTestCase.ScenarioMaker() \
                .given_an_experience() \
                .given_an_scene(description='eco markets', experience_id_of_number=1) \
                .given_an_experience() \
                .given_an_scene(description='science museums', experience_id_of_number=2) \
                .given_an_experience() \
                .given_an_scene(description='ruta del bacalao', experience_id_of_number=3) \
                .when_index_everything_and_search(word='eco') \
                .then_should_return_experiences(['1'])

    def test_search_by_title_accepts_typos(self):
        ExperienceElasticRepoTestCase.ScenarioMaker() \
                .given_an_experience(title='bike routes') \
                .given_an_experience(title='mountein bike') \
                .given_an_experience(title='barcelona restaurants') \
                .given_an_experience(title='romanic monuments') \
                .when_index_everything_and_search(word='mountain') \
                .then_should_return_experiences(['2'])

    def test_search_by_description_accepts_typos(self):
        ExperienceElasticRepoTestCase.ScenarioMaker() \
                .given_an_experience(description='bike routes') \
                .given_an_experience(description='alpinism mountains') \
                .given_an_experience(description='barcelona restaurants') \
                .given_an_experience(description='romanic monuments') \
                .when_index_everything_and_search(word='mountain') \
                .then_should_return_experiences(['2'])

    def test_search_by_scene_title_accepts_typos(self):
        ExperienceElasticRepoTestCase.ScenarioMaker() \
                .given_an_experience() \
                .given_an_scene(title='eko tour', experience_id_of_number=1) \
                .given_an_experience() \
                .given_an_scene(title='science museums', experience_id_of_number=2) \
                .given_an_experience() \
                .given_an_scene(title='ruta del bacalao', experience_id_of_number=3) \
                .when_index_everything_and_search(word='eco') \
                .then_should_return_experiences(['1'])

    def test_search_by_scene_description_accepts_typos(self):
        ExperienceElasticRepoTestCase.ScenarioMaker() \
                .given_an_experience() \
                .given_an_scene(description='ecoo markets', experience_id_of_number=1) \
                .given_an_experience() \
                .given_an_scene(description='science museums', experience_id_of_number=2) \
                .given_an_experience() \
                .given_an_scene(description='ruta del bacalao', experience_id_of_number=3) \
                .when_index_everything_and_search(word='eco') \
                .then_should_return_experiences(['1'])

    def test_search_by_title_sorts_by_length(self):
        ExperienceElasticRepoTestCase.ScenarioMaker() \
                .given_an_experience(title='bike routes') \
                .given_an_experience(title='mountain bike routes for everyone') \
                .given_an_experience(title='mountain') \
                .given_an_experience(title='barcelona restaurants') \
                .given_an_experience(title='romanic monuments') \
                .when_index_everything_and_search(word='mountain') \
                .then_should_return_experiences(['3', '2'])

    def test_search_by_description_sorts_by_length(self):
        ExperienceElasticRepoTestCase.ScenarioMaker() \
                .given_an_experience(description='mountain bike routes') \
                .given_an_experience(description='bike routes') \
                .given_an_experience(description='alpinism mountain') \
                .given_an_experience(description='barcelona restaurants') \
                .given_an_experience(description='romanic monuments') \
                .when_index_everything_and_search(word='mountain') \
                .then_should_return_experiences(['3', '1'])

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
                .then_should_return_experiences(['1', '2'])

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
                .then_should_return_experiences(['4', '1'])

    def test_search_boosts_by_saves_count(self):
        ExperienceElasticRepoTestCase.ScenarioMaker() \
                .given_an_experience(title='bike shopping center', saves_count=1000) \
                .given_an_experience(title='bike tour', saves_count=100) \
                .given_an_experience(title='bike route', saves_count=10000) \
                .when_index_everything_and_search(word='bike') \
                .then_should_return_experiences(['3', '1', '2'])

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
                .then_should_return_experiences(['1', '3', '2'])

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
                .then_should_return_experiences(['1', '3', '2'])

    class ScenarioMaker:

        def __init__(self):
            self.repo = create_experience_elastic_repo()
            self.repo._delete_experience_index()
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

        def when_index_everything_and_search(self, word, location=None):
            for experience in self.experiences:
                experience_scenes = [scene for scene in self.scenes if scene.experience_id == experience.id]
                self.repo.index_experience_and_its_scenes(experience, experience_scenes)
            self.repo._refresh_experience_index()
            self.result = self.repo.search_experiences(word=word, location=location)
            return self

        def then_should_return_experiences(self, experience_ids):
            assert self.result == experience_ids
            return self
