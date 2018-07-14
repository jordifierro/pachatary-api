from mock import Mock

from pachatary.exceptions import InvalidEntityException, EntityDoesNotExistException
from profiles.validators import ProfileValidator
from profiles.entities import Profile


class TestProfileValidator:

    def test_valid_profile(self):
        TestProfileValidator.ScenarioMaker() \
                .given_a_username('usr') \
                .given_a_bio('') \
                .given_a_profile_with_that_params() \
                .given_a_repo_that_raises_entity_does_not_exists() \
                .given_a_profile_validator_with_forbidden_usernames(['ban']) \
                .when_profile_is_validated() \
                .then_result_should_be_true()

    def test_short_username(self):
        TestProfileValidator.ScenarioMaker() \
                .given_a_username('aa') \
                .given_a_bio('') \
                .given_a_profile_with_that_params() \
                .given_a_repo_that_raises_entity_does_not_exists() \
                .given_a_profile_validator_with_forbidden_usernames(['ban']) \
                .when_profile_is_validated() \
                .then_should_raise_invalid_entity_exception_for_wrong_size_username()

    def test_long_username(self):
        TestProfileValidator.ScenarioMaker() \
                .given_a_username('a'*21) \
                .given_a_bio('') \
                .given_a_profile_with_that_params() \
                .given_a_repo_that_raises_entity_does_not_exists() \
                .given_a_profile_validator_with_forbidden_usernames(['ban']) \
                .when_profile_is_validated() \
                .then_should_raise_invalid_entity_exception_for_wrong_size_username()

    def test_wrong_characters_or_order_usernames(self):
        wrong_usernames = ['.asdf', 'asdf.', '_asdf', 'asdf_', 'as..df', 'as_.df', 'as._df', 'as__df',
                           'asdf.', 'asdf_', 'asdfA', 'asdf#', 'asdf?', 'asdf/']
        for username in wrong_usernames:
            TestProfileValidator.ScenarioMaker() \
                .given_a_username(username) \
                .given_a_bio('') \
                .given_a_profile_with_that_params() \
                .given_a_repo_that_raises_entity_does_not_exists() \
                .given_a_profile_validator_with_forbidden_usernames(['ban']) \
                .when_profile_is_validated() \
                .then_should_raise_invalid_entity_exception_for_username()

    def test_forbidden_username(self):
        TestProfileValidator.ScenarioMaker() \
                .given_a_username('ban') \
                .given_a_bio('') \
                .given_a_profile_with_that_params() \
                .given_a_repo_that_raises_entity_does_not_exists() \
                .given_a_profile_validator_with_forbidden_usernames(['ban']) \
                .when_profile_is_validated() \
                .then_should_raise_invalid_entity_exception_for_username()

    def test_username_that_contains_project_name(self):
        TestProfileValidator.ScenarioMaker() \
                .given_a_username('asdf_pachatary_asdf') \
                .given_a_bio('') \
                .given_a_profile_with_that_params() \
                .given_a_repo_that_raises_entity_does_not_exists() \
                .given_a_profile_validator_with_forbidden_usernames(['ban']) \
                .when_profile_is_validated() \
                .then_should_raise_invalid_entity_exception_for_username()

    def test_long_bio(self):
        TestProfileValidator.ScenarioMaker() \
                .given_a_username('usr') \
                .given_a_bio('b'*141) \
                .given_a_profile_with_that_params() \
                .given_a_repo_that_raises_entity_does_not_exists() \
                .given_a_profile_validator_with_forbidden_usernames(['ban']) \
                .when_profile_is_validated() \
                .then_should_raise_invalid_entity_exception_for_wrong_bio()

    def test_already_used_username(self):
        TestProfileValidator.ScenarioMaker() \
                .given_a_username('usr') \
                .given_a_bio('') \
                .given_a_profile_with_that_params() \
                .given_a_second_profile_with_that_params() \
                .given_a_repo_that_returns_second_profile_when_get_by_username() \
                .given_a_profile_validator_with_forbidden_usernames(['ban']) \
                .when_profile_is_validated() \
                .then_should_raise_invalid_entity_exception_for_username()

    def test_already_used_username_by_same_user_is_allowed(self):
        TestProfileValidator.ScenarioMaker() \
                .given_a_username('usr') \
                .given_a_bio('') \
                .given_a_profile_with_that_params() \
                .given_a_repo_that_returns_a_profile_when_get_by_username() \
                .given_a_profile_validator_with_forbidden_usernames(['ban']) \
                .when_profile_is_validated() \
                .then_result_should_be_true()

    class ScenarioMaker:

        def __init__(self):
            self.username = None
            self.bio = None
            self.profile = None
            self.result = None
            self.error = None

        def given_a_username(self, username):
            self.username = username
            return self

        def given_a_bio(self, bio):
            self.bio = bio
            return self

        def given_a_profile_with_that_params(self):
            self.profile = Profile(person_id='1', username=self.username, bio=self.bio)
            return self

        def given_a_second_profile_with_that_params(self):
            self.second_profile = Profile(person_id='2', username=self.username, bio=self.bio)
            return self

        def given_a_profile_validator_with_forbidden_usernames(self, forbidden_usernames):
            self.validator = ProfileValidator(project_name='pachatary', forbidden_usernames=forbidden_usernames,
                                              profile_repo=self.profile_repo)
            return self

        def given_a_repo_that_raises_entity_does_not_exists(self):
            self.profile_repo = Mock()
            self.profile_repo.get_profile.side_effect = EntityDoesNotExistException
            return self

        def given_a_repo_that_returns_a_profile_when_get_by_username(self):
            def fake_get_profile(username=None, logged_person_id=None):
                if username is not None and logged_person_id is not None:
                    return self.profile
                raise EntityDoesNotExistException()

            self.profile_repo = Mock()
            self.profile_repo.get_profile = fake_get_profile
            return self

        def given_a_repo_that_returns_second_profile_when_get_by_username(self):
            def fake_get_profile(username=None, logged_person_id=None):
                if username is not None and logged_person_id is not None:
                    return self.second_profile
                raise EntityDoesNotExistException()

            self.profile_repo = Mock()
            self.profile_repo.get_profile = fake_get_profile
            return self

        def when_profile_is_validated(self):
            try:
                self.result = self.validator.validate(self.profile)
            except Exception as e:
                self.error = e
            return self

        def then_result_should_be_true(self):
            assert self.result is True
            return self

        def then_should_raise_invalid_entity_exception_for_username(self):
            assert type(self.error) is InvalidEntityException
            assert self.error.source == 'username'
            assert self.error.code == 'not_allowed'
            assert str(self.error) == 'Username not allowed'
            return self

        def then_should_raise_invalid_entity_exception_for_wrong_size_username(self):
            assert type(self.error) is InvalidEntityException
            assert self.error.source == 'username'
            assert self.error.code == 'wrong_size'
            assert str(self.error) == 'Username length should be between 1 and 20 chars'
            return self

        def then_should_raise_invalid_entity_exception_for_wrong_bio(self):
            assert type(self.error) is InvalidEntityException
            assert self.error.source == 'bio'
            assert self.error.code == 'wrong_size'
            assert str(self.error) == 'Bio length should not be more than 140 chars'
            return self
