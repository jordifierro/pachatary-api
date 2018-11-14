from mock import Mock

from pachatary.exceptions import NoLoggedException, InvalidEntityException, BlockedContentException
from profiles.entities import Profile
from profiles.interactors import GetProfileInteractor, ModifyProfileInteractor, UploadProfilePictureInteractor


class TestGetProfileInteractor:

    def test_if_no_logged_person_raises_no_logged_person(self):
        TestGetProfileInteractor.ScenarioMaker() \
                .given_a_logged_person_id('0') \
                .given_a_permissions_validator_that_validates(False) \
                .given_a_profile_on_repo('9') \
                .when_execute_interactor(username='usernm') \
                .then_should_validate_person(id='0') \
                .then_should_not_call_repo_get_profile() \
                .then_should_let_no_logged_exception_pass()

    def test_get_self_profile(self):
        TestGetProfileInteractor.ScenarioMaker() \
                .given_a_logged_person_id('8') \
                .given_a_permissions_validator_that_validates(True) \
                .given_a_profile_on_repo('8') \
                .when_execute_interactor(username='self') \
                .then_should_validate_person(id='8') \
                .then_should_call_repo_get_profile_with(person_id='8') \
                .then_should_return_profile()

    def test_get_others_profile(self):
        TestGetProfileInteractor.ScenarioMaker() \
                .given_a_logged_person_id('8') \
                .given_a_permissions_validator_that_validates(True) \
                .given_a_profile_on_repo('9') \
                .given_a_block_repo_that_returns_on_block_exists(False) \
                .when_execute_interactor(username='friend') \
                .then_should_validate_person(id='8') \
                .then_should_call_repo_get_profile_with(username='friend') \
                .then_should_check_if_block_exists('8', '9') \
                .then_should_return_profile()

    def test_get_others_profile_blocked_raises_blocked_content_exception(self):
        TestGetProfileInteractor.ScenarioMaker() \
                .given_a_logged_person_id('8') \
                .given_a_permissions_validator_that_validates(True) \
                .given_a_profile_on_repo('9') \
                .given_a_block_repo_that_returns_on_block_exists(True) \
                .when_execute_interactor(username='friend') \
                .then_should_validate_person(id='8') \
                .then_should_call_repo_get_profile_with(username='friend') \
                .then_should_check_if_block_exists('8', '9') \
                .then_should_raise_blocked_content()

    class ScenarioMaker:

        def __init__(self):
            self.block_repo = Mock()

        def given_a_logged_person_id(self, id):
            self.logged_person_id = id
            return self

        def given_a_permissions_validator_that_validates(self, valid):
            self.permissions_validator = Mock()
            if valid:
                self.permissions_validator.return_value = True
            else:
                self.permissions_validator.validate_permissions.side_effect = NoLoggedException()
            return self

        def given_a_profile_on_repo(self, id):
            self.profile = Profile(person_id=id, username='u', bio='o')
            self.repo = Mock()
            self.repo.get_profile.return_value = self.profile
            return self

        def given_a_block_repo_that_returns_on_block_exists(self, exists):
            self.block_repo.block_exists.return_value = exists
            return self

        def when_execute_interactor(self, username):
            try:
                self.result = GetProfileInteractor(profile_repo=self.repo,
                                                   block_repo=self.block_repo,
                                                   permissions_validator=self.permissions_validator) \
                    .set_params(username=username, logged_person_id=self.logged_person_id).execute()
            except Exception as e:
                self.error = e
            return self

        def then_should_not_call_repo_get_profile(self):
            self.repo.get_profile.assert_not_called()
            return self

        def then_should_call_repo_get_profile_with(self, person_id=None, username=None):
            if person_id is not None:
                self.repo.get_profile.assert_called_once_with(person_id=person_id,
                                                              logged_person_id=self.logged_person_id)
            elif username is not None:
                self.repo.get_profile.assert_called_once_with(username=username,
                                                              logged_person_id=self.logged_person_id)
            return self

        def then_should_validate_person(self, id):
            self.permissions_validator.validate_permissions \
                    .assert_called_once_with(logged_person_id=self.logged_person_id)
            return self

        def then_should_check_if_block_exists(self, creator_id, target_id):
            self.block_repo.block_exists.assert_called_once_with(creator_id=creator_id, target_id=target_id)
            return self

        def then_should_return_profile(self):
            assert self.result == self.profile
            return self

        def then_should_let_no_logged_exception_pass(self):
            assert type(self.error) == NoLoggedException
            return self

        def then_should_raise_blocked_content(self):
            assert type(self.error) == BlockedContentException
            return self


class TestModifyProfileInteractor:

    def test_if_no_logged_person_raises_no_logged_person(self):
        TestModifyProfileInteractor.ScenarioMaker() \
                .given_a_logged_person_id('0') \
                .given_a_permissions_validator_that_validates(False) \
                .given_a_profile_on_repo_for_get() \
                .when_execute_interactor(bio='new bio') \
                .then_should_validate_person(id='0') \
                .then_should_not_call_repo_update_profile() \
                .then_should_raise(NoLoggedException)

    def test_long_bio(self):
        TestModifyProfileInteractor.ScenarioMaker() \
                .given_a_logged_person_id('0') \
                .given_a_permissions_validator_that_validates(True) \
                .given_a_profile_on_repo_for_get() \
                .when_execute_interactor(bio='b'*141) \
                .then_should_validate_person(id='0') \
                .then_should_call_repo_get_profile() \
                .then_should_not_call_repo_update_profile() \
                .then_should_raise(InvalidEntityException)

    def test_correct_update_calls_repo_and_returns(self):
        TestModifyProfileInteractor.ScenarioMaker() \
                .given_a_logged_person_id('8') \
                .given_a_permissions_validator_that_validates(True) \
                .given_a_profile_on_repo_for_get() \
                .given_a_profile_on_repo_for_update() \
                .when_execute_interactor(bio='new bio') \
                .then_should_validate_person(id='8') \
                .then_should_call_repo_get_profile() \
                .then_should_call_repo_update_profile_with(bio='new bio') \
                .then_should_return_updated_profile()

    class ScenarioMaker:

        def given_a_logged_person_id(self, id):
            self.logged_person_id = id
            return self

        def given_a_permissions_validator_that_validates(self, valid):
            self.permissions_validator = Mock()
            if valid:
                self.permissions_validator.return_value = True
            else:
                self.permissions_validator.validate_permissions.side_effect = NoLoggedException()
            return self

        def given_a_profile_on_repo_for_get(self):
            self.profile = Profile(person_id='9', username='u', bio='o')
            self.repo = Mock()
            self.repo.get_profile.return_value = self.profile
            return self

        def given_a_profile_on_repo_for_update(self):
            self.updated_profile = Profile(person_id='2', username='k', bio='m')
            self.repo.update_profile.return_value = self.updated_profile
            return self

        def when_execute_interactor(self, bio):
            try:
                self.result = ModifyProfileInteractor(profile_repo=self.repo,
                                                      permissions_validator=self.permissions_validator) \
                    .set_params(bio=bio, logged_person_id=self.logged_person_id).execute()
            except Exception as e:
                self.error = e
            return self

        def then_should_not_call_repo_get_profile(self):
            self.repo.get_profile.assert_not_called()
            return self

        def then_should_not_call_repo_update_profile(self):
            self.repo.update_profile.assert_not_called()
            return self

        def then_should_call_repo_get_profile(self):
            self.repo.get_profile.assert_called_once_with(person_id=self.logged_person_id,
                                                          logged_person_id=self.logged_person_id)
            return self

        def then_should_call_repo_update_profile_with(self, bio):
            expected_profile = Profile(person_id=self.profile.person_id, username=self.profile.username, bio=bio)
            self.repo.update_profile.assert_called_once_with(expected_profile)
            return self

        def then_should_validate_person(self, id):
            self.permissions_validator.validate_permissions \
                    .assert_called_once_with(logged_person_id=self.logged_person_id)
            return self

        def then_should_return_updated_profile(self):
            assert self.result == self.updated_profile
            return self

        def then_should_raise(self, exception_type):
            assert type(self.error) == exception_type
            return self


class TestUploadProfilePictureInteractor:

    def test_if_no_logged_person_raises_no_logged_person(self):
        TestUploadProfilePictureInteractor.ScenarioMaker() \
                .given_a_logged_person_id('0') \
                .given_a_permissions_validator_that_validates(False) \
                .given_a_profile_repo() \
                .when_execute_interactor(picture='file') \
                .then_should_validate_person(id='0') \
                .then_should_not_call_repo_attach_picture() \
                .then_should_raise(NoLoggedException)

    def test_attaches_picture_to_person_id(self):
        TestUploadProfilePictureInteractor.ScenarioMaker() \
                .given_a_logged_person_id('8') \
                .given_a_permissions_validator_that_validates(True) \
                .given_a_profile_on_repo_attach_picture() \
                .when_execute_interactor(picture='file') \
                .then_should_validate_person(id='8') \
                .then_should_call_repo_attach_picture(picture='file') \
                .then_should_return_profile()

    class ScenarioMaker:

        def given_a_logged_person_id(self, id):
            self.logged_person_id = id
            return self

        def given_a_permissions_validator_that_validates(self, valid):
            self.permissions_validator = Mock()
            if valid:
                self.permissions_validator.return_value = True
            else:
                self.permissions_validator.validate_permissions.side_effect = NoLoggedException()
            return self

        def given_a_profile_repo(self):
            self.repo = Mock()
            return self

        def given_a_profile_on_repo_attach_picture(self):
            self.profile = Profile(person_id='4')
            self.repo = Mock()
            self.repo.attach_picture_to_profile.return_value = self.profile
            return self

        def when_execute_interactor(self, picture):
            try:
                self.result = UploadProfilePictureInteractor(profile_repo=self.repo,
                                                             permissions_validator=self.permissions_validator) \
                    .set_params(picture=picture, logged_person_id=self.logged_person_id).execute()
            except Exception as e:
                self.error = e
            return self

        def then_should_not_call_repo_attach_picture(self):
            self.repo.attach_picture_to_profile.assert_not_called()
            return self

        def then_should_call_repo_attach_picture(self, picture):
            self.repo.attach_picture_to_profile.assert_called_once_with(person_id=self.logged_person_id,
                                                                        picture=picture)
            return self

        def then_should_return_profile(self):
            assert self.result == self.profile
            return self

        def then_should_raise(self, exception_type):
            assert type(self.error) == exception_type
            return self

        def then_should_validate_person(self, id):
            self.permissions_validator.validate_permissions \
                    .assert_called_once_with(logged_person_id=self.logged_person_id)
            return self
