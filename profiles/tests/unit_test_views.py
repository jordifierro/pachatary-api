from mock import Mock

from pachatary.entities import Picture
from profiles.entities import Profile
from profiles.views import ProfileView, UploadProfilePictureView


class TestProfileView:

    def test_returns_profile(self):
        TestProfileView.ScenarioMaker() \
                .given_an_interactor_that_returns_profile() \
                .when_get_is_called(logged_person_id='4', username='self') \
                .then_should_call_interactor_with(logged_person_id='4', username='self') \
                .then_response_should_be_profile_and_200()

    def test_patch_returns_profile_serialized_and_200(self):
        TestProfileView.ScenarioMaker() \
                .given_an_interactor_that_returns_profile() \
                .when_patch_is_called(logged_person_id='3', bio='new bio') \
                .then_should_call_interactor_with(logged_person_id='3', bio='new bio') \
                .then_response_should_be_profile_and_200()

    class ScenarioMaker:

        def given_an_interactor_that_returns_profile(self):
            self.interactor = Mock()
            self.interactor.set_params.return_value = self.interactor
            self.profile = Profile(person_id='4', username='u', bio='b',
                                   picture=Picture(tiny_url='t', small_url='s', medium_url='m'),
                                   is_me=True)
            self.interactor.execute.return_value = self.profile
            return self

        def when_get_is_called(self, logged_person_id, username):
            self.body, self.status = ProfileView(get_profile_interactor=self.interactor) \
                    .get(logged_person_id=logged_person_id, username=username)
            return self

        def when_patch_is_called(self, logged_person_id, bio):
            self.body, self.status = ProfileView(modify_profile_interactor=self.interactor) \
                    .patch(logged_person_id=logged_person_id, bio=bio)
            return self

        def then_should_call_interactor_with(self, logged_person_id, username=None, bio=None):
            if username is not None:
                self.interactor.set_params.assert_called_once_with(logged_person_id=logged_person_id,
                                                                   username=username)
            else:
                self.interactor.set_params.assert_called_once_with(logged_person_id=logged_person_id,
                                                                   bio=bio)
            self.interactor.execute.assert_called_once_with()
            return self

        def then_response_should_be_profile_and_200(self):
            assert self.body == {
                                    'username': self.profile.username,
                                    'bio': self.profile.bio,
                                    'picture': {
                                        'tiny_url': self.profile.picture.tiny_url,
                                        'small_url': self.profile.picture.small_url,
                                        'medium_url': self.profile.picture.medium_url,
                                    },
                                    'is_me': self.profile.is_me,
                                }
            assert self.status == 200
            return self


class TestUploadProfilePictureView:

    def test_post_returns_profile_serialized_and_200(self):
        TestUploadProfilePictureView._ScenarioMaker() \
                .given_a_logged_person_id() \
                .given_a_profile() \
                .given_an_interactor_that_returns_that_profile() \
                .given_a_picture() \
                .when_post_is_called() \
                .then_interactor_receives_params() \
                .then_response_should_be_profile_and_200()

    class _ScenarioMaker:

        def given_a_logged_person_id(self):
            self.logged_person_id = '5'
            return self

        def given_a_profile(self):
            self.profile = Profile(person_id='4', username='u', bio='b',
                                   picture=Picture(tiny_url='t', small_url='s', medium_url='m'),
                                   is_me=True)
            return self

        def given_an_interactor_that_returns_that_profile(self):
            self.interactor_mock = Mock()
            self.interactor_mock.set_params.return_value = self.interactor_mock
            self.interactor_mock.execute.return_value = self.profile
            return self

        def given_a_picture(self):
            self.picture = 'pic'
            return self

        def when_post_is_called(self):
            view = UploadProfilePictureView(upload_profile_picture_interactor=self.interactor_mock)
            self.body, self.status = view.post(picture=self.picture, logged_person_id=self.logged_person_id)
            return self

        def then_interactor_receives_params(self):
            self.interactor_mock.set_params.assert_called_once_with(picture=self.picture,
                                                                    logged_person_id=self.logged_person_id)
            return self

        def then_response_should_be_profile_and_200(self):
            assert self.body == {
                                    'username': self.profile.username,
                                    'bio': self.profile.bio,
                                    'picture': {
                                        'tiny_url': self.profile.picture.tiny_url,
                                        'small_url': self.profile.picture.small_url,
                                        'medium_url': self.profile.picture.medium_url,
                                    },
                                    'is_me': self.profile.is_me,
                                }
            assert self.status == 200
            return self
