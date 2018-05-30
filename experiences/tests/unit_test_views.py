from mock import Mock

from pachatary.entities import Picture
from experiences.entities import Experience
from experiences.views import ExperiencesView, ExperienceView, UploadExperiencePictureView, SaveExperienceView, \
        SearchExperiencesView, ExperienceShareUrlView, TranslateExperienceShareIdView
from experiences.serializers import serialize_experience, serialize_multiple_experiences
from experiences.interactors import SaveUnsaveExperienceInteractor


class TestExperiencesView:

    def test_username_returns_experiences_serialized_and_200(self):
        TestExperiencesView.ScenarioMaker() \
                .given_a_get_experiences_base_url() \
                .given_an_experience_a() \
                .given_an_experience_b() \
                .given_a_next_limit_and_offset() \
                .given_an_interactor_that_returns_that_experiences_and_next_limit_and_offset() \
                .when_get_experiences(logged_person_id='9', username='usr.nm', limit='4', offset='3') \
                .then_should_call_interactor_set_params(logged_person_id='9', username='usr.nm',
                                                        saved=False, limit=4, offset=3) \
                .then_status_code_should_be_200() \
                .then_response_body_should_be_experiences_and_next_url_serialized(username='usr.nm', saved=False)

    def test_saved_returns_experiences_serialized_and_200(self):
        TestExperiencesView.ScenarioMaker() \
                .given_a_get_experiences_base_url() \
                .given_an_experience_a() \
                .given_an_experience_b() \
                .given_a_next_limit_and_offset() \
                .given_an_interactor_that_returns_that_experiences_and_next_limit_and_offset() \
                .when_get_experiences(logged_person_id='9', saved='true', limit='4', offset='3') \
                .then_should_call_interactor_set_params(logged_person_id='9', username=None,
                                                        saved=True, limit=4, offset=3) \
                .then_status_code_should_be_200() \
                .then_response_body_should_be_experiences_and_next_url_serialized(username=None, saved='true')

    class ScenarioMaker:

        def given_a_get_experiences_base_url(self):
            self.experiences_base_url = "base_url"
            return self

        def given_an_experience_a(self):
            picture_a = Picture(small_url='small.a', medium_url='medium.a', large_url='large.a')
            self.experience_a = Experience(id=1, title='A', description='some', picture=picture_a,
                                           author_id='4', author_username='usr', saves_count=4)
            return self

        def given_an_experience_b(self):
            picture_b = Picture(small_url='small.b', medium_url='medium.b', large_url='large.b')
            self.experience_b = Experience(id=2, title='B', description='other', picture=picture_b,
                                           author_id='5', author_username='nms', saves_count=9)
            return self

        def given_a_next_limit_and_offset(self):
            self.next_limit = 8
            self.next_offset = 7
            return self

        def given_an_interactor_that_returns_that_experiences_and_next_limit_and_offset(self):
            self.interactor_mock = Mock()
            self.interactor_mock.set_params.return_value = self.interactor_mock
            self.interactor_mock.execute.return_value = {"results": [self.experience_a, self.experience_b],
                                                         "next_offset": self.next_offset,
                                                         "next_limit": self.next_limit}
            return self

        def when_get_experiences(self, logged_person_id, username=None, saved=None, limit=20, offset=0):
            self.body, self.status = ExperiencesView(get_experiences_interactor=self.interactor_mock,
                                                     get_experiences_base_url=self.experiences_base_url) \
                    .get(logged_person_id=logged_person_id, username=username, saved=saved, limit=limit, offset=offset)
            return self

        def then_should_call_interactor_set_params(self, logged_person_id, username, saved, limit, offset):
            self.interactor_mock.set_params.assert_called_once_with(logged_person_id=logged_person_id,
                                                                    username=username, saved=saved,
                                                                    limit=limit, offset=offset)
            return self

        def then_status_code_should_be_200(self):
            assert self.status == 200
            return self

        def then_response_body_should_be_experiences_and_next_url_serialized(self, saved, username):
            if saved:
                next_url = "{}?saved=true&limit={}&offset={}".format(self.experiences_base_url,
                                                                     self.next_limit, self.next_offset)
            else:
                next_url = "{}?username={}&limit={}&offset={}".format(self.experiences_base_url, username,
                                                                      self.next_limit, self.next_offset)

            assert self.body == {
                "results": serialize_multiple_experiences([self.experience_a, self.experience_b]),
                "next_url": next_url
            }
            return self

    def test_post_returns_experience_serialized_and_200(self):
        experience = Experience(id='1', title='B', description='some',
                                author_id='6', author_username='usr', saves_count=8)

        interactor_mock = Mock()
        interactor_mock.set_params.return_value = interactor_mock
        interactor_mock.execute.return_value = experience

        view = ExperiencesView(create_new_experience_interactor=interactor_mock)
        body, status = view.post(title='B', description='some', logged_person_id='7')

        interactor_mock.set_params.assert_called_once_with(title='B', description='some', logged_person_id='7')
        assert status == 201
        assert body == {
                           'id': '1',
                           'title': 'B',
                           'description': 'some',
                           'picture': None,
                           'author_id': '6',
                           'author_username': 'usr',
                           'is_mine': False,
                           'is_saved': False,
                           'saves_count': 8
                       }


class TestExperienceView:

    def test_patch_returns_experience_serialized_and_200(self):
        experience = Experience(id='1', title='B', description='some',
                                author_id='8', author_username='usrnm', saves_count=8)

        interactor_mock = Mock()
        interactor_mock.set_params.return_value = interactor_mock
        interactor_mock.execute.return_value = experience

        view = ExperienceView(modify_experience_interactor=interactor_mock)
        body, status = view.patch(experience_id='1', description='some', logged_person_id='5')

        interactor_mock.set_params.assert_called_once_with(id='1', title=None, description='some', logged_person_id='5')
        assert status == 200
        assert body == {
                           'id': '1',
                           'title': 'B',
                           'description': 'some',
                           'picture': None,
                           'author_id': '8',
                           'author_username': 'usrnm',
                           'is_mine': False,
                           'is_saved': False,
                           'saves_count': 8
                       }


class TestUploadExperiencePictureView:

    def test_post_returns_experience_serialized_and_200(self):
        TestUploadExperiencePictureView._ScenarioMaker() \
                .given_a_logged_person_id() \
                .given_an_experience() \
                .given_an_interactor_that_returns_that_experience() \
                .given_an_id() \
                .given_a_picture() \
                .when_post_is_called() \
                .then_interactor_receives_params() \
                .then_response_status_is_200() \
                .then_response_body_is_experience_serialized()

    class _ScenarioMaker:

        def __init__(self):
            self._interactor_mock = Mock()
            self._interactor_mock.set_params.return_value = self._interactor_mock
            self._experience = None
            self._id = None
            self._picture = None
            self._response = None
            self._logged_person_id = None

        def given_a_logged_person_id(self):
            self._logged_person_id = '5'
            return self

        def given_an_experience(self):
            self._experience = Experience(id='1', title='B', description='some', author_id='3')
            return self

        def given_an_interactor_that_returns_that_experience(self):
            self._interactor_mock.execute.return_value = self._experience
            return self

        def given_an_id(self):
            self._id = '2'
            return self

        def given_a_picture(self):
            self._picture = 'pic'
            return self

        def when_post_is_called(self):
            view = UploadExperiencePictureView(upload_experience_picture_interactor=self._interactor_mock)
            self._body, self._status = view.post(experience_id=self._id, picture=self._picture,
                                                 logged_person_id=self._logged_person_id)
            return self

        def then_interactor_receives_params(self):
            self._interactor_mock.set_params.assert_called_once_with(experience_id=self._id, picture=self._picture,
                                                                     logged_person_id=self._logged_person_id)
            return self

        def then_response_status_is_200(self):
            assert self._status == 200
            return self

        def then_response_body_is_experience_serialized(self):
            assert self._body == serialize_experience(self._experience)


class TestSaveExperienceView:

    def test_post_returns_201(self):
        TestSaveExperienceView.ScenarioMaker() \
                .given_a_logged_person_id() \
                .given_an_experience_id() \
                .given_an_interactor_that_returns_true() \
                .when_post_is_called() \
                .then_interactor_receives_params_and_action_SAVE() \
                .then_response_status_is_201()

    def test_delete_returns_204(self):
        TestSaveExperienceView.ScenarioMaker() \
                .given_a_logged_person_id() \
                .given_an_experience_id() \
                .given_an_interactor_that_returns_true() \
                .when_delete_is_called() \
                .then_interactor_receives_params_and_action_UNSAVE() \
                .then_response_status_is_204()

    class ScenarioMaker:

        def given_a_logged_person_id(self):
            self.logged_person_id = '5'
            return self

        def given_an_experience_id(self):
            self.experience_id = '6'
            return self

        def given_an_interactor_that_returns_true(self):
            self.interactor_mock = Mock()
            self.interactor_mock.execute.return_value = True
            return self

        def when_post_is_called(self):
            view = SaveExperienceView(save_unsave_experience_interactor=self.interactor_mock)
            self.body, self.status = view.post(experience_id=self.experience_id, logged_person_id=self.logged_person_id)
            return self

        def when_delete_is_called(self):
            view = SaveExperienceView(save_unsave_experience_interactor=self.interactor_mock)
            self.body, self.status = view.delete(experience_id=self.experience_id,
                                                 logged_person_id=self.logged_person_id)
            return self

        def then_interactor_receives_params_and_action_SAVE(self):
            self.interactor_mock.set_params.assert_called_once_with(action=SaveUnsaveExperienceInteractor.Action.SAVE,
                                                                    experience_id=self.experience_id,
                                                                    logged_person_id=self.logged_person_id)
            return self

        def then_interactor_receives_params_and_action_UNSAVE(self):
            self.interactor_mock.set_params.assert_called_once_with(action=SaveUnsaveExperienceInteractor.Action.UNSAVE,
                                                                    experience_id=self.experience_id,
                                                                    logged_person_id=self.logged_person_id)
            return self

        def then_response_status_is_204(self):
            assert self.status == 204
            return self

        def then_response_status_is_201(self):
            assert self.status == 201
            return self


class TestSearchExperiencesView:

    def test_returns_experiences_serialized_and_200(self):
        TestSearchExperiencesView.ScenarioMaker() \
                .given_a_search_experiences_base_url() \
                .given_an_experience_a() \
                .given_an_experience_b() \
                .given_a_next_limit_and_offset() \
                .given_an_interactor_that_returns_that_experiences_and_next_limit_and_offset() \
                .when_search_experiences(logged_person_id='9', word='culture', latitude='9.43',
                                         longitude='-4.88', limit='4', offset='3') \
                .then_should_call_interactor_set_params(logged_person_id='9', word='culture',
                                                        location=(9.43, -4.88), limit='4', offset='3') \
                .then_status_code_should_be_200() \
                .then_response_body_should_be_experiences_and_next_url_serialized(word='culture', latitude='9.43',
                                                                                  longitude='-4.88')

    def test_no_latitude_calls_with_location_none(self):
        TestSearchExperiencesView.ScenarioMaker() \
                .given_a_search_experiences_base_url() \
                .given_an_experience_a() \
                .given_an_experience_b() \
                .given_a_next_limit_and_offset() \
                .given_an_interactor_that_returns_that_experiences_and_next_limit_and_offset() \
                .when_search_experiences(logged_person_id='9', word='culture', latitude=None,
                                         longitude='-4.88', limit='4', offset='3') \
                .then_should_call_interactor_set_params(logged_person_id='9', word='culture',
                                                        location=None, limit='4', offset='3') \
                .then_status_code_should_be_200() \
                .then_response_body_should_be_experiences_and_next_url_serialized(word='culture', latitude=None,
                                                                                  longitude='-4.88')

    def test_no_longitude_calls_with_location_none(self):
        TestSearchExperiencesView.ScenarioMaker() \
                .given_a_search_experiences_base_url() \
                .given_an_experience_a() \
                .given_an_experience_b() \
                .given_a_next_limit_and_offset() \
                .given_an_interactor_that_returns_that_experiences_and_next_limit_and_offset() \
                .when_search_experiences(logged_person_id='9', word='culture', latitude='9.43',
                                         longitude=None, limit='4', offset='3') \
                .then_should_call_interactor_set_params(logged_person_id='9', word='culture',
                                                        location=None, limit='4', offset='3') \
                .then_status_code_should_be_200() \
                .then_response_body_should_be_experiences_and_next_url_serialized(word='culture', latitude='9.43',
                                                                                  longitude=None)

    def test_empty_word_calls_with_word_none(self):
        TestSearchExperiencesView.ScenarioMaker() \
                .given_a_search_experiences_base_url() \
                .given_an_experience_a() \
                .given_an_experience_b() \
                .given_a_next_limit_and_offset() \
                .given_an_interactor_that_returns_that_experiences_and_next_limit_and_offset() \
                .when_search_experiences(logged_person_id='9', word='', latitude='9.43',
                                         longitude=None, limit='4', offset='3') \
                .then_should_call_interactor_set_params(logged_person_id='9', word=None,
                                                        location=None, limit='4', offset='3') \
                .then_status_code_should_be_200() \
                .then_response_body_should_be_experiences_and_next_url_serialized(word=None, latitude='9.43',
                                                                                  longitude=None)

    class ScenarioMaker:

        def given_a_search_experiences_base_url(self):
            self.experiences_base_url = "base_url"
            return self

        def given_an_experience_a(self):
            picture_a = Picture(small_url='small.a', medium_url='medium.a', large_url='large.a')
            self.experience_a = Experience(id=1, title='A', description='some', picture=picture_a,
                                           author_id='4', author_username='usr', saves_count=4)
            return self

        def given_an_experience_b(self):
            picture_b = Picture(small_url='small.b', medium_url='medium.b', large_url='large.b')
            self.experience_b = Experience(id=2, title='B', description='other', picture=picture_b,
                                           author_id='5', author_username='nms', saves_count=9)
            return self

        def given_a_next_limit_and_offset(self):
            self.next_limit = 8
            self.next_offset = 7
            return self

        def given_an_interactor_that_returns_that_experiences_and_next_limit_and_offset(self):
            self.interactor_mock = Mock()
            self.interactor_mock.set_params.return_value = self.interactor_mock
            self.interactor_mock.execute.return_value = {"results": [self.experience_a, self.experience_b],
                                                         "next_offset": self.next_offset,
                                                         "next_limit": self.next_limit}
            return self

        def when_search_experiences(self, logged_person_id, word, latitude, longitude, limit, offset):
            self.body, self.status = SearchExperiencesView(search_experiences_interactor=self.interactor_mock,
                                                           search_experiences_base_url=self.experiences_base_url) \
                    .get(logged_person_id=logged_person_id, word=word,
                         latitude=latitude, longitude=longitude, limit=limit, offset=offset)
            return self

        def then_should_call_interactor_set_params(self, logged_person_id, word, location, limit, offset):
            self.interactor_mock.set_params.assert_called_once_with(logged_person_id=logged_person_id, word=word,
                                                                    location=location, limit=int(limit),
                                                                    offset=int(offset))
            return self

        def then_status_code_should_be_200(self):
            assert self.status == 200
            return self

        def then_response_body_should_be_experiences_and_next_url_serialized(self, word, latitude, longitude):
            next_url = '{}?offset={}&limit={}'.format(self.experiences_base_url, self.next_offset, self.next_limit)
            if word is not None:
                next_url = '{}&word={}'.format(next_url, word)
            if latitude is not None:
                next_url = '{}&latitude={}'.format(next_url, latitude)
            if longitude is not None:
                next_url = '{}&longitude={}'.format(next_url, longitude)

            assert self.body == {
                'results': serialize_multiple_experiences([self.experience_a, self.experience_b]),
                'next_url': next_url
            }
            return self


class TestExperienceShareUrlView:

    def test_returns_url_with_share_id(self):
        TestExperienceShareUrlView.ScenarioMaker() \
                .given_a_public_url('pachatary.com') \
                .given_an_interactor_that_returns(share_id='Ab1dR14') \
                .when_get_is_called(logged_person_id='4', experience_id='5') \
                .then_should_call_interactor_with(logged_person_id='4', experience_id='5') \
                .then_response_should_be({'share_url': 'pachatary.com/e/Ab1dR14'}, 200)

    class ScenarioMaker:

        def given_a_public_url(self, url):
            self.url = url
            return self

        def given_an_interactor_that_returns(self, share_id):
            self.interactor = Mock()
            self.interactor.set_params.return_value = self.interactor
            self.interactor.execute.return_value = share_id
            return self

        def when_get_is_called(self, logged_person_id, experience_id):
            self.body, self.status = ExperienceShareUrlView(
                base_url=self.url, get_or_create_experience_share_id_interactor=self.interactor) \
                    .get(logged_person_id=logged_person_id, experience_id=experience_id)
            return self

        def then_should_call_interactor_with(self, logged_person_id, experience_id):
            self.interactor.set_params.assert_called_once_with(logged_person_id=logged_person_id,
                                                               experience_id=experience_id)
            self.interactor.execute.assert_called_once_with()
            return self

        def then_response_should_be(self, body, status):
            assert self.body == body
            assert self.status == status
            return self


class TestTranslateExperienceShareIdView:

    def test_returns_id(self):
        TestTranslateExperienceShareIdView.ScenarioMaker() \
                .given_an_interactor_that_returns('9') \
                .when_get_is_called(logged_person_id='4', experience_share_id='asdf1234') \
                .then_should_call_interactor_with(logged_person_id='4', experience_share_id='asdf1234') \
                .then_response_should_be({'experience_id': '9'}, 200)

    class ScenarioMaker:

        def given_an_interactor_that_returns(self, id):
            self.interactor = Mock()
            self.interactor.set_params.return_value = self.interactor
            self.interactor.execute.return_value = id
            return self

        def when_get_is_called(self, logged_person_id, experience_share_id):
            self.body, self.status = TranslateExperienceShareIdView(
                get_experience_id_from_share_id_interactor=self.interactor) \
                    .get(logged_person_id=logged_person_id, experience_share_id=experience_share_id)
            return self

        def then_should_call_interactor_with(self, logged_person_id, experience_share_id):
            self.interactor.set_params.assert_called_once_with(logged_person_id=logged_person_id,
                                                               experience_share_id=experience_share_id)
            self.interactor.execute.assert_called_once_with()
            return self

        def then_response_should_be(self, body, status):
            assert self.body == body
            assert self.status == status
            return self
