from mock import Mock, call

from pachatary.exceptions import InvalidEntityException, EntityDoesNotExistException, NoLoggedException, \
        NoPermissionException, ConflictException, BlockedContentException
from profiles.entities import Profile
from experiences.entities import Experience
from experiences.interactors import GetExperiencesInteractor, CreateNewExperienceInteractor, \
        ModifyExperienceInteractor, UploadExperiencePictureInteractor, SaveUnsaveExperienceInteractor, \
        SearchExperiencesInteractor, GetOrCreateExperienceShareIdInteractor, IdGenerator, \
        GetExperienceInteractor, FlagExperienceInteractor


class TestGetExperiences:

    def test_get_self_returns_repo_response(self):
        TestGetExperiences.ScenarioMaker() \
                .given_an_experience() \
                .given_an_experience() \
                .given_a_repo_that_returns_experiences_and_offset(7) \
                .given_a_permission_validator_that_returns_true() \
                .when_interactor_is_executed(logged_person_id='2', username='self', offset=4,
                                             limit=GetExperiencesInteractor.MAX_PAGINATE_LIMIT + 1) \
                .then_should_call_get_person_experiences_with(logged_person_id='2', target_person_id='2', offset=4,
                                                              limit=GetExperiencesInteractor.MAX_PAGINATE_LIMIT) \
                .then_validate_permissions_should_be_called_with(logged_person_id='2') \
                .then_result_should_be_experiences_and_next_offset_limit(
                        offset=7, limit=GetExperiencesInteractor.MAX_PAGINATE_LIMIT)

    def test_get_others_returns_repo_response(self):
        TestGetExperiences.ScenarioMaker() \
                .given_an_experience() \
                .given_an_experience() \
                .given_a_repo_that_returns_experiences_and_offset(7) \
                .given_a_profile_interactor_that_returns_other_person_with_id('13') \
                .given_a_permission_validator_that_returns_true() \
                .when_interactor_is_executed(logged_person_id='2', username='usr.nm', offset=4,
                                             limit=GetExperiencesInteractor.MAX_PAGINATE_LIMIT + 1) \
                .then_should_call_get_profile_interactor_with_username('usr.nm', logged_person_id='2') \
                .then_should_call_get_person_experiences_with(logged_person_id='2', target_person_id='13', offset=4,
                                                              limit=GetExperiencesInteractor.MAX_PAGINATE_LIMIT) \
                .then_validate_permissions_should_be_called_with(logged_person_id='2') \
                .then_result_should_be_experiences_and_next_offset_limit(
                        offset=7, limit=GetExperiencesInteractor.MAX_PAGINATE_LIMIT)

    def test_get_saved_returns_repo_response(self):
        TestGetExperiences.ScenarioMaker() \
                .given_an_experience() \
                .given_an_experience() \
                .given_a_repo_that_returns_experiences_and_offset(7) \
                .given_a_permission_validator_that_returns_true() \
                .when_interactor_is_executed(logged_person_id='2', saved=True, offset=4,
                                             limit=GetExperiencesInteractor.MAX_PAGINATE_LIMIT + 1) \
                .then_should_call_get_saved_experiences_with(logged_person_id='2', offset=4,
                                                             limit=GetExperiencesInteractor.MAX_PAGINATE_LIMIT) \
                .then_validate_permissions_should_be_called_with(logged_person_id='2') \
                .then_result_should_be_experiences_and_next_offset_limit(
                        offset=7, limit=GetExperiencesInteractor.MAX_PAGINATE_LIMIT)

    def test_no_logged_raises_exception(self):
        TestGetExperiences.ScenarioMaker() \
                .given_a_permission_validator_that_raises_exception() \
                .when_interactor_is_executed(logged_person_id='2', saved=True, offset=4, limit=3) \
                .then_validate_permissions_should_be_called_with(logged_person_id='2') \
                .then_should_raise_no_logged_exception()

    class ScenarioMaker:

        def __init__(self):
            self.experiences = []
            self.repo = Mock()
            self.get_profile_interactor = Mock()

        def given_an_experience(self):
            self.experiences.append(Experience(id=len(self.experiences)+1, title='t', description='d',
                                               picture=None, author_id='1'))
            return self

        def given_a_repo_that_returns_experiences_and_offset(self, offset):
            self.repo.get_person_experiences.return_value = {'results': self.experiences, 'next_offset': offset}
            self.repo.get_saved_experiences.return_value = {'results': self.experiences, 'next_offset': offset}
            return self

        def given_a_permission_validator_that_returns_true(self):
            self.permissions_validator = Mock()
            self.permissions_validator.validate_permissions.return_value = True
            return self

        def given_a_permission_validator_that_raises_exception(self):
            self.permissions_validator = Mock()
            self.permissions_validator.validate_permissions.side_effect = NoLoggedException()
            return self

        def given_a_profile_interactor_that_returns_other_person_with_id(self, person_id):
            self.get_profile_interactor.set_params.return_value = self.get_profile_interactor
            self.get_profile_interactor.execute.return_value = Profile(person_id=person_id)
            return self

        def when_interactor_is_executed(self, logged_person_id, saved=False, username=None, offset=0, limit=20):
            try:
                self.result = GetExperiencesInteractor(experience_repo=self.repo,
                                                       get_profile_interactor=self.get_profile_interactor,
                                                       permissions_validator=self.permissions_validator) \
                        .set_params(username=username, saved=saved,
                                    logged_person_id=logged_person_id, offset=offset, limit=limit).execute()
            except Exception as e:
                self.error = e
            return self

        def then_should_call_get_person_experiences_with(self, logged_person_id, target_person_id, offset, limit):
            self.repo.get_person_experiences.assert_called_once_with(logged_person_id=logged_person_id,
                                                                     target_person_id=target_person_id,
                                                                     offset=offset, limit=limit)
            return self

        def then_should_call_get_saved_experiences_with(self, logged_person_id, offset, limit):
            self.repo.get_saved_experiences.assert_called_once_with(logged_person_id=logged_person_id,
                                                                    offset=offset, limit=limit)
            return self

        def then_should_call_get_profile_interactor_with_username(self, username, logged_person_id):
            self.get_profile_interactor.set_params.assert_called_once_with(username=username,
                                                                           logged_person_id=logged_person_id)
            self.get_profile_interactor.execute.assert_called_once_with()
            return self

        def then_validate_permissions_should_be_called_with(self, logged_person_id):
            self.permissions_validator.validate_permissions.assert_called_once_with(logged_person_id=logged_person_id)
            return self

        def then_result_should_be_experiences_and_next_offset_limit(self, offset, limit):
            assert self.result == {'results': self.experiences, 'next_offset': offset, 'next_limit': limit}
            return self

        def then_should_raise_no_logged_exception(self):
            assert type(self.error) is NoLoggedException
            return self


class TestSearchExperiences:

    def test_returns_repo_response(self):
        TestSearchExperiences.ScenarioMaker() \
                .given_a_logged_person_id() \
                .given_a_search_word() \
                .given_a_location() \
                .given_a_pagination_limit_and_offset() \
                .given_a_permission_validator_that_returns_true() \
                .given_an_experience() \
                .given_another_experience() \
                .given_a_next_offset() \
                .given_a_repo_that_returns_both_experiences_and_next_offset() \
                .given_a_block_repo_that_returns_on_get_blocked_people([]) \
                .when_interactor_is_executed() \
                .then_should_call_search_experiences_word_location_and_limit_and_offset() \
                .then_validate_permissions_should_be_called_with_logged_person_id() \
                .then_result_should_be_both_experiences_and_next_offset_and_same_limit()

    def test_filters_experiences_from_blocked_people(self):
        TestSearchExperiences.ScenarioMaker() \
                .given_a_logged_person_id() \
                .given_a_search_word() \
                .given_a_location() \
                .given_a_pagination_limit_and_offset() \
                .given_a_permission_validator_that_returns_true() \
                .given_an_experience() \
                .given_another_experience() \
                .given_a_next_offset() \
                .given_a_repo_that_returns_both_experiences_and_next_offset_and_other_experiences_from('44') \
                .given_a_block_repo_that_returns_on_get_blocked_people(['44']) \
                .when_interactor_is_executed() \
                .then_should_call_search_experiences_word_location_and_limit_and_offset() \
                .then_validate_permissions_should_be_called_with_logged_person_id() \
                .then_result_should_be_both_experiences_and_next_offset_and_same_limit()

    def test_when_limit_is_higher_that_interactor_maximum(self):
        TestSearchExperiences.ScenarioMaker() \
                .given_a_logged_person_id() \
                .given_a_search_word() \
                .given_a_location() \
                .given_a_big_pagination_limit_and_offset() \
                .given_a_permission_validator_that_returns_true() \
                .given_an_experience() \
                .given_another_experience() \
                .given_a_next_offset() \
                .given_a_repo_that_returns_both_experiences_and_next_offset() \
                .given_a_block_repo_that_returns_on_get_blocked_people([]) \
                .when_interactor_is_executed() \
                .then_should_call_search_experiences_with_params_but_limit_at_20() \
                .then_validate_permissions_should_be_called_with_logged_person_id() \
                .then_result_should_be_both_experiences_and_next_offset_and_limit_20()

    def test_no_logged_raises_exception(self):
        TestSearchExperiences.ScenarioMaker() \
                .given_a_permission_validator_that_raises_exception() \
                .given_a_block_repo_that_returns_on_get_blocked_people([]) \
                .when_interactor_is_executed() \
                .then_validate_permissions_should_be_called_with_logged_person_id() \
                .then_should_raise_no_logged_exception()

    class ScenarioMaker:

        def __init__(self):
            self.logged_person_id = None
            self.experience_repo = None
            self.word = None
            self.location = None
            self.limit = 0
            self.offset = 0

        def given_a_logged_person_id(self):
            self.logged_person_id = '0'
            return self

        def given_a_search_word(self):
            self.word = 'culture'
            return self

        def given_a_location(self):
            self.location = (4.5, -0.8)
            return self

        def given_a_pagination_limit_and_offset(self):
            self.limit = 7
            self.offset = 4
            return self

        def given_a_big_pagination_limit_and_offset(self):
            self.limit = 25
            self.offset = 4
            return self

        def given_an_experience(self):
            self.experience_a = Experience(id=1, title='A', description='some', picture=None, author_id='1')
            return self

        def given_another_experience(self):
            self.experience_b = Experience(id=2, title='B', description='other', picture=None, author_id='1')
            return self

        def given_a_next_offset(self):
            self.next_offset = 7
            return self

        def given_a_permission_validator_that_returns_true(self):
            self.permissions_validator = Mock()
            self.permissions_validator.validate_permissions.return_value = True
            return self

        def given_a_permission_validator_that_raises_exception(self):
            self.permissions_validator = Mock()
            self.permissions_validator.validate_permissions.side_effect = NoLoggedException()
            return self

        def given_a_repo_that_returns_both_experiences_and_next_offset(self):
            self.experience_repo = Mock()
            self.experience_repo.search_experiences.return_value = {"results": [self.experience_a, self.experience_b],
                                                                    "next_offset": self.next_offset}
            return self

        def given_a_repo_that_returns_both_experiences_and_next_offset_and_other_experiences_from(self, author_id):
            exp_a = Experience(id=5, title='T1', description='d1', picture=None, author_id=author_id)
            exp_b = Experience(id=6, title='T2', description='d2', picture=None, author_id=author_id)
            exp_c = Experience(id=7, title='T3', description='d3', picture=None, author_id=author_id)
            self.experience_repo = Mock()
            self.experience_repo.search_experiences.return_value = {
                    "results": [exp_a, self.experience_a, exp_b, self.experience_b, exp_c],
                    "next_offset": self.next_offset
                }
            return self

        def given_a_block_repo_that_returns_on_get_blocked_people(self, people):
            self.block_repo = Mock()
            self.block_repo.get_blocked_people.return_value = people
            return self

        def when_interactor_is_executed(self):
            try:
                self.response = SearchExperiencesInteractor(experience_repo=self.experience_repo,
                                                            block_repo=self.block_repo,
                                                            permissions_validator=self.permissions_validator) \
                        .set_params(word=self.word, location=self.location, logged_person_id=self.logged_person_id,
                                    limit=self.limit, offset=self.offset).execute()
            except Exception as e:
                print()
                print(e)
                print()
                self.error = e
            return self

        def then_result_should_be_both_experiences_and_next_offset_and_same_limit(self):
            assert self.response == {"results": [self.experience_a, self.experience_b],
                                     "next_offset": self.next_offset,
                                     "next_limit": self.limit}
            return self

        def then_result_should_be_both_experiences_and_next_offset_and_limit_20(self):
            assert self.response == {"results": [self.experience_a, self.experience_b],
                                     "next_offset": self.next_offset,
                                     "next_limit": 20}
            return self

        def then_should_call_search_experiences_word_location_and_limit_and_offset(self):
            self.experience_repo.search_experiences.assert_called_once_with(self.logged_person_id,
                                                                            word=self.word, location=self.location,
                                                                            limit=self.limit, offset=self.offset)
            return self

        def then_should_call_search_experiences_with_params_but_limit_at_20(self):
            self.experience_repo.search_experiences.assert_called_once_with(self.logged_person_id,
                                                                            word=self.word, location=self.location,
                                                                            limit=20, offset=self.offset)
            return self

        def then_validate_permissions_should_be_called_with_logged_person_id(self):
            self.permissions_validator.validate_permissions \
                    .assert_called_once_with(logged_person_id=self.logged_person_id)
            return self

        def then_should_raise_no_logged_exception(self):
            assert type(self.error) is NoLoggedException
            return self


class TestCreateNewExperience:

    def test_creates_and_returns_experience(self):
        TestCreateNewExperience.ScenarioMaker() \
                .given_a_logged_person_id() \
                .given_an_experience() \
                .given_an_experience_repo_that_returns_that_experience_on_create() \
                .given_a_permissions_validator_that_returns_true() \
                .given_a_title() \
                .given_a_description() \
                .given_an_author_id() \
                .given_an_experience_validator_that_accepts_them() \
                .when_execute_interactor() \
                .then_result_should_be_the_experience() \
                .then_should_validate_permissions() \
                .then_repo_create_method_should_be_called_with_params() \
                .then_params_should_be_validated()

    def test_invalid_experience_returns_error_and_doesnt_create_it(self):
        TestCreateNewExperience.ScenarioMaker() \
                .given_a_logged_person_id() \
                .given_an_experience() \
                .given_an_experience_repo() \
                .given_a_title() \
                .given_a_description() \
                .given_an_author_id() \
                .given_a_permissions_validator_that_returns_true() \
                .given_an_experience_validator_that_raises_invalid_entity_exception() \
                .when_execute_interactor() \
                .then_should_raise_invalid_entity_exception() \
                .then_should_validate_permissions() \
                .then_params_should_be_validated() \
                .then_repo_create_method_should_not_be_called()

    def test_no_permissions_raises_exception(self):
        TestCreateNewExperience.ScenarioMaker() \
                .given_a_logged_person_id() \
                .given_an_experience() \
                .given_an_experience_repo() \
                .given_a_title() \
                .given_a_description() \
                .given_an_author_id() \
                .given_a_permissions_validator_that_raises_no_permission_exception() \
                .given_an_experience_validator_that_raises_invalid_entity_exception() \
                .when_execute_interactor() \
                .then_should_raise_no_permissions_exception() \
                .then_should_validate_permissions() \
                .then_repo_create_method_should_not_be_called()

    class ScenarioMaker:

        def __init__(self):
            self.author_id = None

        def given_a_logged_person_id(self):
            self.logged_person_id = '5'
            return self

        def given_an_experience(self):
            self.experience = Experience(title='Title', description='', author_id='3')
            return self

        def given_an_experience_repo_that_returns_that_experience_on_create(self):
            self.experience_repo = Mock()
            self.experience_repo.create_experience.return_value = self.experience
            return self

        def given_a_title(self):
            self.title = 'Title'
            return self

        def given_a_description(self):
            self.description = 'desc'
            return self

        def given_an_author_id(self):
            self.author_id = '4'
            return self

        def given_an_experience_repo(self):
            self.experience_repo = Mock()
            return self

        def given_a_permissions_validator_that_returns_true(self):
            self.permissions_validator = Mock()
            self.permissions_validator.validate_permissions.return_value = True
            return self

        def given_a_permissions_validator_that_raises_no_permission_exception(self):
            self.permissions_validator = Mock()
            self.permissions_validator.validate_permissions.side_effect = NoPermissionException()
            return self

        def given_an_experience_validator_that_accepts_them(self):
            self.experience_validator = Mock()
            self.experience_validator.validate_experience.return_value = True
            return self

        def given_an_experience_validator_that_raises_invalid_entity_exception(self):
            self.experience_validator = Mock()
            self.experience_validator.validate_experience.side_effect = \
                InvalidEntityException(source='title', code='empty_attribute',
                                       message='Title must be between 1 and 20 chars')
            return self

        def when_execute_interactor(self):
            try:
                self.response = CreateNewExperienceInteractor(self.experience_repo,
                                                              self.experience_validator, self.permissions_validator) \
                    .set_params(title=self.title, description=self.description,
                                logged_person_id=self.logged_person_id).execute()
            except Exception as e:
                self.error = e
            return self

        def then_result_should_be_the_experience(self):
            assert self.response == self.experience
            return self

        def then_should_raise_invalid_entity_exception(self):
            assert type(self.error) is InvalidEntityException
            assert self.error.source == 'title'
            assert self.error.code == 'empty_attribute'
            assert str(self.error) == 'Title must be between 1 and 20 chars'
            return self

        def then_repo_create_method_should_be_called_with_params(self):
            experience_params = Experience(title=self.title, description=self.description,
                                           author_id=self.logged_person_id)
            self.experience_repo.create_experience.assert_called_once_with(experience_params)
            return self

        def then_repo_create_method_should_not_be_called(self):
            self.experience_repo.create_experience.assert_not_called()
            return self

        def then_params_should_be_validated(self):
            experience_params = Experience(title=self.title, description=self.description,
                                           author_id=self.logged_person_id)
            self.experience_validator.validate_experience.assert_called_once_with(experience_params)
            return self

        def then_should_validate_permissions(self):
            self.permissions_validator.validate_permissions \
                    .assert_called_once_with(logged_person_id=self.logged_person_id, wants_to_create_content=True)
            return self

        def then_should_raise_no_permissions_exception(self):
            assert type(self.error) is NoPermissionException
            return self


class TestModifyExperience:

    def test_gets_modifies_not_none_params_and_returns_experience(self):
        TestModifyExperience.ScenarioMaker() \
                .given_an_experience() \
                .given_an_id() \
                .given_a_description() \
                .given_a_logged_person_id() \
                .given_a_permissions_validator_that_returns_true() \
                .given_another_experience_updated_with_that_params() \
                .given_an_experience_repo_that_returns_both_experiences_on_get_and_update() \
                .given_an_experience_validator_that_accepts() \
                .when_interactor_is_executed() \
                .then_result_should_be_second_experience() \
                .then_should_validate_permissions() \
                .then_get_experience_should_be_called_with_id_and_logged_person_id() \
                .then_experience_validation_should_be_called_with_updated_experience() \
                .then_update_experience_should_be_called_with_updated_experience()

    def test_invalid_experience_returns_error_and_doesnt_update_it(self):
        TestModifyExperience.ScenarioMaker() \
                .given_an_id() \
                .given_a_description() \
                .given_a_logged_person_id() \
                .given_a_permissions_validator_that_returns_true() \
                .given_an_experience() \
                .given_another_experience_updated_with_that_params() \
                .given_an_experience_repo_that_returns_that_experience_on_get() \
                .given_an_experience_validator_that_raises_invalid_entity_exception() \
                .when_interactor_is_executed() \
                .then_should_raise_invalid_entity_exception() \
                .then_should_validate_permissions() \
                .then_get_experience_should_be_called_with_id_and_logged_person_id() \
                .then_experience_validation_should_be_called_with_updated_experience() \
                .then_update_experience_should_be_not_called()

    def test_unexistent_experience_returns_entity_does_not_exist_error(self):
        TestModifyExperience.ScenarioMaker() \
                .given_an_id() \
                .given_a_description() \
                .given_a_logged_person_id() \
                .given_a_permissions_validator_that_returns_true() \
                .given_an_experience_repo_that_raises_entity_does_not_exist() \
                .given_an_experience_validator() \
                .when_interactor_is_executed() \
                .then_should_raise_entity_does_not_exists() \
                .then_should_validate_permissions() \
                .then_get_experience_should_be_called_with_id_and_logged_person_id() \
                .then_update_experience_should_be_not_called()

    def test_no_permissions_raises_expcetion(self):
        TestModifyExperience.ScenarioMaker() \
                .given_an_id() \
                .given_a_description() \
                .given_a_logged_person_id() \
                .given_a_permissions_validator_that_raises_no_permissions_exception() \
                .given_an_experience_repo_that_raises_entity_does_not_exist() \
                .given_an_experience_validator() \
                .when_interactor_is_executed() \
                .then_should_raise_no_permissions_exception() \
                .then_should_validate_permissions() \
                .then_update_experience_should_be_not_called()

    class ScenarioMaker:

        def given_an_experience(self):
            self.experience = Experience(id='1', title='Title', description='some', author_id='2')
            return self

        def given_an_id(self):
            self.id = '1'
            return self

        def given_a_description(self):
            self.description = ''
            return self

        def given_a_logged_person_id(self):
            self.logged_person_id = '2'
            return self

        def given_a_permissions_validator_that_returns_true(self):
            self.permissions_validator = Mock()
            self.permissions_validator.validate_permissions.return_value = True
            return self

        def given_a_permissions_validator_that_raises_no_permissions_exception(self):
            self.permissions_validator = Mock()
            self.permissions_validator.validate_permissions.side_effect = NoPermissionException()
            return self

        def given_another_experience_updated_with_that_params(self):
            self.updated_experience = Experience(id=self.experience.id, title=self.experience.title,
                                                 description=self.description, author_id=self.experience.author_id)
            return self

        def given_an_experience_repo_that_returns_both_experiences_on_get_and_update(self):
            self.experience_repo = Mock()
            self.experience_repo.get_experience.return_value = self.experience
            self.experience_repo.update_experience.return_value = self.updated_experience
            return self

        def given_an_experience_repo_that_returns_that_experience_on_get(self):
            self.experience_repo = Mock()
            self.experience_repo.get_experience.return_value = self.experience
            return self

        def given_an_experience_repo_that_raises_entity_does_not_exist(self):
            self.experience_repo = Mock()
            self.experience_repo.get_experience.side_effect = EntityDoesNotExistException()
            return self

        def given_an_experience_validator(self):
            self.experience_validator = Mock()
            return self

        def given_an_experience_validator_that_accepts(self):
            self.experience_validator = Mock()
            self.experience_validator.validate_experience.return_value = True
            return self

        def given_an_experience_validator_that_raises_invalid_entity_exception(self):
            self.experience_validator = Mock()
            self.experience_validator.validate_experience.side_effect = \
                InvalidEntityException(source='title', code='empty_attribute',
                                       message='Title must be between 1 and 20 chars')
            return self

        def when_interactor_is_executed(self):
            try:
                self.result = ModifyExperienceInteractor(self.experience_repo, self.experience_validator,
                                                         self.permissions_validator) \
                    .set_params(id=self.id, title=None, description=self.description,
                                logged_person_id=self.logged_person_id).execute()
            except Exception as e:
                self.error = e
            return self

        def then_result_should_be_second_experience(self):
            assert self.result == self.updated_experience
            return self

        def then_get_experience_should_be_called_with_id_and_logged_person_id(self):
            self.experience_repo.get_experience \
                    .assert_called_once_with(id=self.id, logged_person_id=self.logged_person_id)
            return self

        def then_experience_validation_should_be_called_with_updated_experience(self):
            self.experience_validator.validate_experience.assert_called_once_with(self.updated_experience)
            return self

        def then_update_experience_should_be_called_with_updated_experience(self):
            self.experience_repo.update_experience.assert_called_once_with(
                    self.updated_experience, logged_person_id=self.logged_person_id)
            return self

        def then_update_experience_should_be_not_called(self):
            self.experience_repo.update_experience.assert_not_called()
            return self

        def then_should_raise_invalid_entity_exception(self):
            assert type(self.error) is InvalidEntityException
            assert self.error.source == 'title'
            assert self.error.code == 'empty_attribute'
            assert str(self.error) == 'Title must be between 1 and 20 chars'
            return self

        def then_should_raise_entity_does_not_exists(self):
            assert type(self.error) is EntityDoesNotExistException
            return self

        def then_should_validate_permissions(self):
            self.permissions_validator.validate_permissions \
                    .assert_called_once_with(logged_person_id=self.logged_person_id,
                                             has_permissions_to_modify_experience=self.id)
            return self

        def then_should_raise_no_permissions_exception(self):
            assert type(self.error) is NoPermissionException
            return self


class TestUploadExperiencePictureInteractor:

    def test_validates_permissions_and_attach_picture_to_experience(self):
        TestUploadExperiencePictureInteractor.ScenarioMaker() \
                .given_a_logged_person_id() \
                .given_a_permissions_validator_that_returns_true() \
                .given_an_experience() \
                .given_an_experience_repo_that_returns_that_experience_on_attach() \
                .given_an_experience_id() \
                .given_a_picture() \
                .when_interactor_is_executed() \
                .then_should_validate_permissions() \
                .then_should_call_repo_attach_picture_to_experience() \
                .then_should_return_experience()

    def test_invalid_permissions_doesnt_attach_picture(self):
        TestUploadExperiencePictureInteractor.ScenarioMaker() \
                .given_a_logged_person_id() \
                .given_a_permissions_validator_that_raises_no_permissions_exception() \
                .given_an_experience_repo() \
                .given_an_experience_id() \
                .given_a_picture() \
                .when_interactor_is_executed() \
                .then_should_validate_permissions() \
                .then_should_not_call_repo_attach_picture_to_experience() \
                .then_should_raise_no_permissions_exception()

    class ScenarioMaker:

        def given_a_logged_person_id(self):
            self.logged_person_id = '9'
            return self

        def given_a_permissions_validator_that_returns_true(self):
            self.permissions_validator = Mock()
            self.permissions_validator.validate_permissions.return_value = True
            return self

        def given_a_permissions_validator_that_raises_no_permissions_exception(self):
            self.permissions_validator = Mock()
            self.permissions_validator.validate_permissions.side_effect = NoPermissionException
            return self

        def given_an_experience(self):
            self.experience = Experience(id='2', title='T', description='s', author_id='4')
            return self

        def given_an_experience_repo_that_returns_that_experience_on_attach(self):
            self.experience_repo = Mock()
            self.experience_repo.attach_picture_to_experience.return_value = self.experience
            return self

        def given_an_experience_repo(self):
            self.experience_repo = Mock()
            return self

        def given_an_experience_id(self):
            self.experience_id = '5'
            return self

        def given_a_picture(self):
            self.picture = 'pic'
            return self

        def when_interactor_is_executed(self):
            try:
                interactor = UploadExperiencePictureInteractor(experience_repo=self.experience_repo,
                                                               permissions_validator=self.permissions_validator)
                self.result = interactor.set_params(experience_id=self.experience_id, picture=self.picture,
                                                    logged_person_id=self.logged_person_id).execute()
            except Exception as e:
                self.error = e
            return self

        def then_should_validate_permissions(self):
            self.permissions_validator.validate_permissions \
                    .assert_called_once_with(logged_person_id=self.logged_person_id,
                                             has_permissions_to_modify_experience=self.experience_id)
            return self

        def then_should_call_repo_attach_picture_to_experience(self):
            self.experience_repo.attach_picture_to_experience.assert_called_once_with(experience_id=self.experience_id,
                                                                                      picture=self.picture)
            return self

        def then_should_return_experience(self):
            assert self.result == self.experience
            return self

        def then_should_not_call_repo_attach_picture_to_experience(self):
            self.experience_repo.attach_picture_to_experience.assert_not_called()
            return self

        def then_should_raise_no_permissions_exception(self):
            assert type(self.error) is NoPermissionException
            return self


class TestSaveUnsaveExperienceInteractor:

    def test_unauthorized_raises_no_logged_exception(self):
        TestSaveUnsaveExperienceInteractor.ScenarioMaker() \
                .given_a_permissions_validator_that_raises_no_permissions_exception() \
                .given_an_experience_repo_that_returns_true_on_save() \
                .given_a_get_experience_interactor_that_returns_others_experience() \
                .when_interactor_is_executed(action=SaveUnsaveExperienceInteractor.Action.SAVE) \
                .then_should_not_call_repo_save_experience() \
                .then_should_raise_no_logged_exception()

    def test_save_you_own_experience_raises_conflict_exception(self):
        TestSaveUnsaveExperienceInteractor.ScenarioMaker() \
                .given_a_logged_person_id() \
                .given_a_permissions_validator_that_returns_true() \
                .given_an_experience_id() \
                .given_a_get_experience_interactor_that_returns_own_experience() \
                .given_an_experience_repo_that_returns_true_on_save() \
                .when_interactor_is_executed(action=SaveUnsaveExperienceInteractor.Action.SAVE) \
                .then_should_validate_permissions() \
                .then_should_call_interactor_with_experience_id_and_logged_person_id() \
                .then_should_not_call_repo_save_experience() \
                .then_should_raise_conflict_exception()

    def test_save_calls_repo_save_and_returns_true(self):
        TestSaveUnsaveExperienceInteractor.ScenarioMaker() \
                .given_a_logged_person_id() \
                .given_a_permissions_validator_that_returns_true() \
                .given_an_experience_id() \
                .given_an_experience_repo_that_returns_true_on_save() \
                .given_a_get_experience_interactor_that_returns_others_experience() \
                .when_interactor_is_executed(action=SaveUnsaveExperienceInteractor.Action.SAVE) \
                .then_should_validate_permissions() \
                .then_should_call_interactor_with_experience_id_and_logged_person_id() \
                .then_should_call_repo_save_experience_with_person_id() \
                .then_should_return_true()

    def test_unsave_calls_repo_unsave_and_returns_true(self):
        TestSaveUnsaveExperienceInteractor.ScenarioMaker() \
                .given_a_logged_person_id() \
                .given_a_permissions_validator_that_returns_true() \
                .given_an_experience_id() \
                .given_an_experience_repo_that_returns_true_on_save() \
                .given_a_get_experience_interactor_that_returns_others_experience() \
                .when_interactor_is_executed(action=SaveUnsaveExperienceInteractor.Action.UNSAVE) \
                .then_should_validate_permissions() \
                .then_should_call_interactor_with_experience_id_and_logged_person_id() \
                .then_should_call_repo_unsave_experience_with_person_id() \


    class ScenarioMaker:

        def __init__(self):
            self.experience_id = None
            self.logged_person_id = None

        def given_a_logged_person_id(self):
            self.logged_person_id = '9'
            return self

        def given_a_permissions_validator_that_returns_true(self):
            self.permissions_validator = Mock()
            self.permissions_validator.validate_permissions.return_value = True
            return self

        def given_a_permissions_validator_that_raises_no_permissions_exception(self):
            self.permissions_validator = Mock()
            self.permissions_validator.validate_permissions.side_effect = NoLoggedException
            return self

        def given_an_experience_repo_that_returns_true_on_save(self):
            self.experience_repo = Mock()
            self.experience_repo.save_experience.return_value = True
            return self

        def given_a_get_experience_interactor_that_returns_own_experience(self):
            own_experience = Experience(id='4', title='t', description='d', author_id=self.logged_person_id)
            self.get_experience_interactor = Mock()
            self.get_experience_interactor.set_params.return_value = self.get_experience_interactor
            self.get_experience_interactor.execute.return_value = own_experience
            return self

        def given_a_get_experience_interactor_that_returns_others_experience(self):
            others_experience = Experience(id='4', title='t', description='d', author_id='3')
            self.get_experience_interactor = Mock()
            self.get_experience_interactor.set_params.return_value = self.get_experience_interactor
            self.get_experience_interactor.execute.return_value = others_experience
            return self

        def given_an_experience_repo_that_returns_true_on_unsave(self):
            self.experience_repo = Mock()
            self.experience_repo.unsave_experience.return_value = True
            return self

        def given_an_experience_id(self):
            self.experience_id = '5'
            return self

        def when_interactor_is_executed(self, action):
            try:
                interactor = SaveUnsaveExperienceInteractor(experience_repo=self.experience_repo,
                                                            permissions_validator=self.permissions_validator,
                                                            get_experience_interactor=self.get_experience_interactor)
                self.result = interactor.set_params(action=action, experience_id=self.experience_id,
                                                    logged_person_id=self.logged_person_id).execute()
            except Exception as e:
                self.error = e
            return self

        def then_should_validate_permissions(self):
            self.permissions_validator.validate_permissions \
                    .assert_called_once_with(logged_person_id=self.logged_person_id)
            return self

        def then_should_call_interactor_with_experience_id_and_logged_person_id(self):
            self.get_experience_interactor.set_params.assert_called_once_with(experience_id=self.experience_id,
                                                                              logged_person_id=self.logged_person_id)
            self.get_experience_interactor.execute.assert_called_once_with()
            return self

        def then_should_call_repo_save_experience_with_person_id(self):
            self.experience_repo.save_experience.assert_called_once_with(experience_id=self.experience_id,
                                                                         person_id=self.logged_person_id)
            return self

        def then_should_call_repo_unsave_experience_with_person_id(self):
            self.experience_repo.unsave_experience.assert_called_once_with(experience_id=self.experience_id,
                                                                           person_id=self.logged_person_id)
            return self

        def then_should_return_true(self):
            assert self.result is True
            return self

        def then_should_not_call_repo_save_experience(self):
            self.experience_repo.save_experience.assert_not_called()
            return self

        def then_should_raise_no_logged_exception(self):
            assert type(self.error) is NoLoggedException
            return self

        def then_should_raise_conflict_exception(self):
            assert type(self.error) is ConflictException
            assert self.error.source == 'experience'
            assert self.error.code == 'self_save'
            assert str(self.error) == 'You cannot save your own experiences'
            return self


class TestGetOrCreateExperienceShareIdInteractor:

    def test_if_no_logged_person_raises_no_logged_person(self):
        TestGetOrCreateExperienceShareIdInteractor.ScenarioMaker() \
                .given_a_logged_person_id('0') \
                .given_a_permissions_validator_that_raises_no_logged() \
                .given_an_experience_on_interactor(id='4') \
                .when_execute_interactor() \
                .then_should_let_no_logged_exception_pass()

    def test_if_already_has_id_returns_id(self):
        TestGetOrCreateExperienceShareIdInteractor.ScenarioMaker() \
                .given_a_logged_person_id('5') \
                .given_a_permissions_validator_that_validates() \
                .given_an_experience_on_interactor(id='4', share_id='asdf') \
                .when_execute_interactor() \
                .then_should_get_experience(id='4') \
                .then_should_validate_person(id='5') \
                .then_should_return(share_id='asdf')

    def test_if_hasnt_share_id_creates_updates_and_return(self):
        TestGetOrCreateExperienceShareIdInteractor.ScenarioMaker() \
                .given_a_logged_person_id('5') \
                .given_a_permissions_validator_that_validates() \
                .given_an_experience_on_interactor(id='4') \
                .given_a_share_id_generator_that_returns(share_ids=['qwerty']) \
                .given_an_experience_repo_that_raises_conflict_when_update(share_id='none') \
                .when_execute_interactor() \
                .then_should_get_experience(id='4') \
                .then_should_validate_person(id='5') \
                .then_should_update_experience_with(share_ids=['qwerty']) \
                .then_should_return(share_id='qwerty')

    def test_when_colission_tries_new_share_id(self):
        TestGetOrCreateExperienceShareIdInteractor.ScenarioMaker() \
                .given_a_logged_person_id('5') \
                .given_a_permissions_validator_that_validates() \
                .given_an_experience_on_interactor(id='4') \
                .given_a_share_id_generator_that_returns(share_ids=['qwerty', 'other']) \
                .given_an_experience_repo_that_raises_conflict_when_update(share_id='qwerty') \
                .when_execute_interactor() \
                .then_should_get_experience(id='4') \
                .then_should_validate_person(id='5') \
                .then_should_update_experience_with(share_ids=['qwerty', 'other']) \
                .then_should_return(share_id='other')

    class ScenarioMaker:

        def __init__(self):
            self.repo = Mock()
            self.permissions_validator = Mock()
            self.id_generator = Mock()

        def given_a_logged_person_id(self, id):
            self.logged_person_id = id
            return self

        def given_a_permissions_validator_that_validates(self):
            self.permissions_validator.return_value = True
            return self

        def given_a_permissions_validator_that_raises_no_logged(self):
            self.permissions_validator.validate_permissions.side_effect = NoLoggedException()
            return self

        def given_an_experience_on_interactor(self, id, share_id=None):
            self.experience = Experience(id=id, title='as', description='er', author_id='9', share_id=share_id)
            self.get_experience_interactor = Mock()
            self.get_experience_interactor.set_params.return_value = self.get_experience_interactor
            self.get_experience_interactor.execute.return_value = self.experience
            return self

        def given_a_share_id_generator_that_returns(self, share_ids):
            self.id_generator.generate.side_effect = share_ids
            return self

        def given_an_experience_repo_that_raises_conflict_when_update(self, share_id):

            def update_experience(experience):
                if experience.share_id == share_id:
                    raise ConflictException(source='s', code='c', message='m')
                return experience

            self.repo.update_experience.side_effect = update_experience
            return self

        def when_execute_interactor(self):
            try:
                self.result = \
                    GetOrCreateExperienceShareIdInteractor(experience_repo=self.repo,
                                                           permissions_validator=self.permissions_validator,
                                                           id_generator=self.id_generator,
                                                           get_experience_interactor=self.get_experience_interactor) \
                    .set_params(experience_id=self.experience.id, logged_person_id=self.logged_person_id).execute()
            except Exception as e:
                self.error = e
            return self

        def then_should_validate_person(self, id):
            self.permissions_validator.validate_permissions \
                    .assert_called_once_with(logged_person_id=self.logged_person_id)
            return self

        def then_should_get_experience(self, id):
            self.get_experience_interactor.set_params.assert_called_once_with(experience_id=id,
                                                                              logged_person_id=self.logged_person_id)
            self.get_experience_interactor.execute.assert_called_once_with()
            return self

        def then_should_return(self, share_id):
            assert self.result == share_id
            return self

        def then_should_update_experience_with(self, share_ids):
            updated_experiences = [self.experience.builder().share_id(share_id).build() for share_id in share_ids]
            self.repo.updated_experience.mock_calls = [call(x) for x in updated_experiences]
            return self

        def then_should_let_no_logged_exception_pass(self):
            assert type(self.error) == NoLoggedException
            return self


class TestIdGenerator:

    def test_length_should_be_8(self):
        TestIdGenerator.ScenarioMaker() \
                .when_generate() \
                .result_should_be_string_8_long()

    def test_generate_different_each_time(self):
        TestIdGenerator.ScenarioMaker() \
                .when_generate_2() \
                .results_should_be_different()

    class ScenarioMaker:

        def when_generate(self):
            self.result = IdGenerator().generate()
            return self

        def when_generate_2(self):
            self.result_a = IdGenerator().generate()
            self.result_b = IdGenerator().generate()
            return self

        def result_should_be_string_8_long(self):
            assert len(self.result) == 8
            return self

        def results_should_be_different(self):
            assert self.result_a != self.result_b
            return self


class TestGetExperienceInteractor:

    def test_if_no_logged_person_raises_no_logged_person(self):
        TestGetExperienceInteractor.ScenarioMaker() \
                .given_a_logged_person_id('0') \
                .given_a_permissions_validator_that_raises_no_logged() \
                .given_an_experience_on_repo(id='4') \
                .given_a_block_repo_that_returns(False) \
                .when_execute_interactor(id='4') \
                .then_should_validate_person(id='0') \
                .then_should_let_no_logged_exception_pass()

    def test_given_an_id_returns_experience(self):
        TestGetExperienceInteractor.ScenarioMaker() \
                .given_a_logged_person_id('8') \
                .given_a_permissions_validator_that_validates() \
                .given_an_experience_on_repo(id='4', author_id='10') \
                .given_a_block_repo_that_returns(False) \
                .when_execute_interactor(id='4') \
                .then_should_validate_person(id='8') \
                .then_should_call_repo_get_experience_with(id='4') \
                .then_should_check_block_exists('8', '10') \
                .then_should_return_experience()

    def test_given_a_blocked_author_raises_exception(self):
        TestGetExperienceInteractor.ScenarioMaker() \
                .given_a_logged_person_id('8') \
                .given_a_permissions_validator_that_validates() \
                .given_an_experience_on_repo(id='4', author_id='10') \
                .given_a_block_repo_that_returns(True) \
                .when_execute_interactor(id='4') \
                .then_should_validate_person(id='8') \
                .then_should_call_repo_get_experience_with(id='4') \
                .then_should_check_block_exists('8', '10') \
                .then_should_raise_blocked_content_exception()

    def test_given_a_share_id_returns_experience(self):
        TestGetExperienceInteractor.ScenarioMaker() \
                .given_a_logged_person_id('3') \
                .given_a_permissions_validator_that_validates() \
                .given_an_experience_on_repo(share_id='s8H', author_id='10') \
                .given_a_block_repo_that_returns(False) \
                .when_execute_interactor(share_id='s8H') \
                .then_should_validate_person(id='3') \
                .then_should_call_repo_get_experience_with(share_id='s8H') \
                .then_should_check_block_exists('3', '10') \
                .then_should_return_experience()

    class ScenarioMaker:

        def given_a_logged_person_id(self, id):
            self.logged_person_id = id
            return self

        def given_a_permissions_validator_that_validates(self):
            self.permissions_validator = Mock()
            self.permissions_validator.return_value = True
            return self

        def given_a_permissions_validator_that_raises_no_logged(self):
            self.permissions_validator = Mock()
            self.permissions_validator.validate_permissions.side_effect = NoLoggedException()
            return self

        def given_an_experience_on_repo(self, id=None, share_id=None, author_id='9'):
            if id is not None:
                self.experience = Experience(id=id, title='as', description='er', author_id=author_id)
            elif share_id is not None:
                self.experience = Experience(id='789', title='as', description='er',
                                             author_id=author_id, share_id=share_id)
            self.repo = Mock()
            self.repo.get_experience.return_value = self.experience
            return self

        def given_a_block_repo_that_returns(self, exists):
            self.block_repo = Mock()
            self.block_repo.block_exists.return_value = exists
            return self

        def when_execute_interactor(self, id=None, share_id=None):
            try:
                if id is not None:
                    self.result = GetExperienceInteractor(experience_repo=self.repo,
                                                          block_repo=self.block_repo,
                                                          permissions_validator=self.permissions_validator) \
                        .set_params(experience_id=id, logged_person_id=self.logged_person_id).execute()
                elif share_id is not None:
                    self.result = GetExperienceInteractor(experience_repo=self.repo,
                                                          block_repo=self.block_repo,
                                                          permissions_validator=self.permissions_validator) \
                        .set_params(experience_share_id=share_id, logged_person_id=self.logged_person_id).execute()
            except Exception as e:
                self.error = e
            return self

        def then_should_call_repo_get_experience_with(self, id=None, share_id=None):
            if id is not None:
                self.repo.get_experience.assert_called_once_with(id=id, logged_person_id=self.logged_person_id)
            elif share_id is not None:
                self.repo.get_experience.assert_called_once_with(share_id=share_id,
                                                                 logged_person_id=self.logged_person_id)
            return self

        def then_should_validate_person(self, id):
            self.permissions_validator.validate_permissions \
                    .assert_called_once_with(logged_person_id=self.logged_person_id)
            return self

        def then_should_check_block_exists(self, creator_id, target_id):
            self.block_repo.block_exists.assert_called_once_with(creator_id=creator_id, target_id=target_id)
            return self

        def then_should_return_experience(self):
            assert self.result == self.experience
            return self

        def then_should_let_no_logged_exception_pass(self):
            assert type(self.error) == NoLoggedException
            return self

        def then_should_raise_blocked_content_exception(self):
            assert type(self.error) == BlockedContentException
            return self


class TestFlagExperienceInteractor:

    def test_if_no_logged_person_raises_no_logged_person(self):
        TestFlagExperienceInteractor.ScenarioMaker() \
                .given_a_permissions_validator_that_raises_no_logged() \
                .given_an_experience_repo_that_returns_true_on_flag() \
                .when_execute_interactor(logged_person_id='0', experience_id='5', reason='Spam') \
                .then_should_validate_person(id='0') \
                .then_should_let_no_logged_exception_pass()

    def test_flags_experience(self):
        TestFlagExperienceInteractor.ScenarioMaker() \
                .given_a_permissions_validator_that_validates() \
                .given_an_experience_repo_that_returns_true_on_flag() \
                .when_execute_interactor(logged_person_id='8', experience_id='5', reason='Spam') \
                .then_should_validate_person(id='8') \
                .then_should_call_get_experience_interactor(experience_id='5', logged_person_id='8') \
                .then_should_call_repo_flag_experience_with(person_id='8', experience_id='5', reason='Spam') \
                .then_should_return_true()

    class ScenarioMaker:

        def __init__(self):
            self.get_experience_interactor = Mock()
            self.get_experience_interactor.set_params.return_value = self.get_experience_interactor

        def given_a_permissions_validator_that_validates(self):
            self.permissions_validator = Mock()
            self.permissions_validator.return_value = True
            return self

        def given_a_permissions_validator_that_raises_no_logged(self):
            self.permissions_validator = Mock()
            self.permissions_validator.validate_permissions.side_effect = NoLoggedException()
            return self

        def given_an_experience_repo_that_returns_true_on_flag(self):
            self.repo = Mock()
            self.repo.flag_experience.return_value = True
            return self

        def when_execute_interactor(self, logged_person_id, experience_id, reason):
            try:
                self.result = FlagExperienceInteractor(experience_repo=self.repo,
                                                       permissions_validator=self.permissions_validator,
                                                       get_experience_interactor=self.get_experience_interactor) \
                    .set_params(logged_person_id=logged_person_id, experience_id=experience_id, reason=reason).execute()
            except Exception as e:
                self.error = e
            return self

        def then_should_call_repo_flag_experience_with(self, person_id, experience_id, reason):
            self.repo.flag_experience.assert_called_once_with(person_id=person_id,
                                                              experience_id=experience_id, reason=reason)
            return self

        def then_should_validate_person(self, id):
            self.permissions_validator.validate_permissions \
                    .assert_called_once_with(logged_person_id=id)
            return self

        def then_should_call_get_experience_interactor(self, experience_id, logged_person_id):
            self.get_experience_interactor.set_params.assert_called_once_with(experience_id=experience_id,
                                                                              logged_person_id=logged_person_id)
            self.get_experience_interactor.execute.assert_called_once_with()
            return self

        def then_should_return_true(self):
            assert self.result is True
            return self

        def then_should_let_no_logged_exception_pass(self):
            assert type(self.error) == NoLoggedException
            return self
