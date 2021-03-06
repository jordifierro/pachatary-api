from mock import Mock, call

from pachatary.exceptions import InvalidEntityException, EntityDoesNotExistException, NoLoggedException, \
        NoPermissionException
from scenes.interactors import GetScenesFromExperienceInteractor, CreateNewSceneInteractor, ModifySceneInteractor, \
        UploadScenePictureInteractor, IndexExperiencesInteractor
from scenes.entities import Scene
from experiences.entities import Experience


class TestGetScenesFromExperience:

    def test_returns_scenes(self):
        TestGetScenesFromExperience.ScenarioMaker() \
                .given_a_logged_person_id() \
                .given_a_permissions_validator_that_returns_true() \
                .given_two_scenes() \
                .given_scene_repo_that_returns_both() \
                .given_a_get_experience_interactor() \
                .given_an_experience_id() \
                .when_interactor_is_executed() \
                .then_permissions_should_be_validated() \
                .then_get_scenes_should_be_called_with_experience_id() \
                .then_should_call_get_experience_interactor() \
                .then_result_should_be_both_scenes_sorted_by_id()

    def test_no_logged_returns_exception(self):
        TestGetScenesFromExperience.ScenarioMaker() \
                .given_a_logged_person_id() \
                .given_a_permissions_validator_that_raises_no_logged_exception() \
                .given_a_get_experience_interactor() \
                .given_two_scenes() \
                .given_scene_repo_that_returns_both() \
                .given_an_experience_id() \
                .when_interactor_is_executed() \
                .then_permissions_should_be_validated() \
                .then_should_raise_no_permissions_exception()

    class ScenarioMaker:

        def given_a_logged_person_id(self):
            self.logged_person_id = '4'
            return self

        def given_a_permissions_validator_that_returns_true(self):
            self.permissions_validator = Mock()
            self.permissions_validator.validate_permissions.return_value = True
            return self

        def given_a_permissions_validator_that_raises_no_logged_exception(self):
            self.permissions_validator = Mock()
            self.permissions_validator.validate_permissions.side_effect = NoLoggedException()
            return self

        def given_a_get_experience_interactor(self):
            self.get_experience_interactor = Mock()
            self.get_experience_interactor.set_params.return_value = self.get_experience_interactor
            return self

        def given_two_scenes(self):
            self.scene_a = Scene(id=3, title='', description='', picture=None, latitude=1, longitude=0, experience_id=1)
            self.scene_b = Scene(id=2, title='', description='', picture=None, latitude=1, longitude=0, experience_id=1)
            return self

        def given_scene_repo_that_returns_both(self):
            self.scene_repo = Mock()
            self.scene_repo.get_scenes.return_value = [self.scene_a, self.scene_b]
            return self

        def given_an_experience_id(self):
            self.experience_id = '5'
            return self

        def when_interactor_is_executed(self):
            try:
                self.result = GetScenesFromExperienceInteractor(self.scene_repo, self.get_experience_interactor,
                                                                permissions_validator=self.permissions_validator) \
                        .set_params(experience_id=self.experience_id, logged_person_id=self.logged_person_id).execute()
            except Exception as e:
                self.error = e
            return self

        def then_get_scenes_should_be_called_with_experience_id(self):
            self.scene_repo.get_scenes.assert_called_once_with(experience_id=self.experience_id)
            return self

        def then_should_call_get_experience_interactor(self):
            self.get_experience_interactor.set_params.assert_called_once_with(logged_person_id=self.logged_person_id,
                                                                              experience_id=self.experience_id)
            self.get_experience_interactor.execute.assert_called_once_with()
            return self

        def then_result_should_be_both_scenes_sorted_by_id(self):
            assert self.result == [self.scene_b, self.scene_a]
            return self

        def then_permissions_should_be_validated(self):
            self.permissions_validator.validate_permissions \
                    .assert_called_once_with(logged_person_id=self.logged_person_id)
            return self

        def then_should_raise_no_permissions_exception(self):
            assert type(self.error) is NoLoggedException
            return self


class TestCreateNewScene:

    def test_creates_and_returns_scene(self):
        TestCreateNewScene.ScenarioMaker() \
                .given_a_logged_person_id() \
                .given_a_permissions_validator_that_returns_true() \
                .given_a_title() \
                .given_a_description() \
                .given_a_latitude() \
                .given_a_longitude() \
                .given_an_experience_id() \
                .given_an_scene_validator_that_accepts_that_scene() \
                .given_an_scene() \
                .given_an_scene_repo_that_returns_scene_on_create() \
                .given_an_reindex_experience_method() \
                .when_interactor_is_executed() \
                .then_validate_permissions_is_called_with_logged_person_id_and_experience_id() \
                .then_validate_scene_is_called_with_previous_params() \
                .then_create_scene_is_called_with_previous_params() \
                .then_should_call_reindex_experience_method_with_experience_id() \
                .then_result_should_be_scene()

    def test_invalid_scene_returns_error_and_doesnt_create_it(self):
        TestCreateNewScene.ScenarioMaker() \
                .given_a_logged_person_id() \
                .given_a_permissions_validator_that_returns_true() \
                .given_a_title() \
                .given_a_description() \
                .given_a_latitude() \
                .given_a_longitude() \
                .given_an_experience_id() \
                .given_an_scene_validator_that_raises_invalid_params() \
                .given_an_scene_repo() \
                .given_an_reindex_experience_method() \
                .when_interactor_is_executed() \
                .then_validate_permissions_is_called_with_logged_person_id_and_experience_id() \
                .then_validate_scene_is_called_with_previous_params() \
                .then_create_scene_should_not_be_called() \
                .then_should_raise_invalid_entity_exception()

    def test_invalid_permissions_returns_error(self):
        TestCreateNewScene.ScenarioMaker() \
                .given_a_logged_person_id() \
                .given_a_permissions_validator_that_raises_no_permissions_exception() \
                .given_a_title() \
                .given_a_description() \
                .given_a_latitude() \
                .given_a_longitude() \
                .given_an_experience_id() \
                .given_an_scene_validator_that_raises_invalid_params() \
                .given_an_scene_repo() \
                .given_an_reindex_experience_method() \
                .when_interactor_is_executed() \
                .then_validate_permissions_is_called_with_logged_person_id_and_experience_id() \
                .then_create_scene_should_not_be_called() \
                .then_should_raise_no_permissions_exception()

    class ScenarioMaker:

        def given_a_logged_person_id(self):
            self.logged_person_id = '8'
            return self

        def given_a_permissions_validator_that_returns_true(self):
            self.permissions_validator = Mock()
            self.permissions_validator.validate_permissions.return_value = True
            return self

        def given_a_permissions_validator_that_raises_no_permissions_exception(self):
            self.permissions_validator = Mock()
            self.permissions_validator.validate_permissions.side_effect = NoPermissionException()
            return self

        def given_an_reindex_experience_method(self):
            self.reindex_experience = Mock()
            return self

        def given_a_title(self):
            self.title = 'Title'
            return self

        def given_a_description(self):
            self.description = 'description'
            return self

        def given_a_latitude(self):
            self.latitude = 1
            return self

        def given_a_longitude(self):
            self.longitude = 0
            return self

        def given_an_experience_id(self):
            self.experience_id = '9'
            return self

        def given_an_scene(self):
            self.created_scene = Scene(title='Title', description='', latitude=1, longitude=0, experience_id='1')
            return self

        def given_an_scene_validator_that_accepts_that_scene(self):
            self.scene_validator = Mock()
            self.scene_validator.validate_scene.return_value = True
            return self

        def given_an_scene_validator_that_raises_invalid_params(self):
            self.scene_validator = Mock()
            self.scene_validator.validate_scene.side_effect = InvalidEntityException(source='s', code='c', message='m')
            return self

        def given_an_scene_repo_that_returns_scene_on_create(self):
            self.scene_repo = Mock()
            self.scene_repo.create_scene.return_value = self.created_scene
            return self

        def given_an_scene_repo(self):
            self.scene_repo = Mock()
            return self

        def when_interactor_is_executed(self):
            try:
                self.result = CreateNewSceneInteractor(self.scene_repo, self.scene_validator,
                                                       self.permissions_validator, self.reindex_experience) \
                    .set_params(title=self.title, description=self.description, latitude=self.latitude,
                                longitude=self.longitude, experience_id=self.experience_id,
                                logged_person_id=self.logged_person_id).execute()
            except Exception as e:
                self.error = e
            return self

        def then_validate_permissions_is_called_with_logged_person_id_and_experience_id(self):
            self.permissions_validator.validate_permissions \
                    .assert_called_once_with(logged_person_id=self.logged_person_id,
                                             has_permissions_to_modify_experience=self.experience_id)
            return self

        def then_validate_scene_is_called_with_previous_params(self):
            scene = Scene(title=self.title, description=self.description, latitude=self.latitude,
                          longitude=self.longitude, experience_id=self.experience_id)
            self.scene_validator.validate_scene.assert_called_once_with(scene)
            return self

        def then_create_scene_is_called_with_previous_params(self):
            scene = Scene(title=self.title, description=self.description, latitude=self.latitude,
                          longitude=self.longitude, experience_id=self.experience_id)
            self.scene_repo.create_scene.assert_called_once_with(scene)
            return self

        def then_create_scene_should_not_be_called(self):
            self.scene_repo.created_scene.assert_not_called()
            return self

        def then_result_should_be_scene(self):
            assert self.result == self.created_scene

        def then_should_raise_invalid_entity_exception(self):
            assert type(self.error) is InvalidEntityException
            assert self.error.source == 's'
            assert self.error.code == 'c'
            assert str(self.error) == 'm'
            return self

        def then_should_raise_no_permissions_exception(self):
            assert type(self.error) is NoPermissionException
            return self

        def then_should_call_reindex_experience_method_with_experience_id(self):
            self.reindex_experience.assert_called_once_with(self.experience_id)
            return self


class TestModifyScene:

    def test_gets_modifies_not_none_params_and_returns_scene(self):
        TestModifyScene.ScenarioMaker() \
                .given_a_logged_person_id() \
                .given_a_permissions_validator_that_returns_true() \
                .given_an_scene() \
                .given_an_scene_repo() \
                .given_that_scene_repo_returns_that_scene_on_get() \
                .given_an_updated_scene() \
                .given_that_scene_repo_returns_that_scene_on_update() \
                .given_an_scene_validator_that_accepts() \
                .given_an_id() \
                .given_a_description() \
                .given_a_longitude() \
                .when_interactor_is_executed() \
                .then_permissions_should_be_validated() \
                .then_get_scene_should_be_called_with_id() \
                .then_scene_with_new_description_an_longitude_should_be_validated() \
                .then_update_scene_should_be_called_with_new_description_an_longitude() \
                .then_result_should_be_updated_scene()

    def test_invalid_scene_returns_error_and_doesnt_update_it(self):
        TestModifyScene.ScenarioMaker() \
                .given_a_logged_person_id() \
                .given_a_permissions_validator_that_returns_true() \
                .given_an_scene() \
                .given_an_scene_repo() \
                .given_that_scene_repo_returns_that_scene_on_get() \
                .given_an_scene_validator_that_raises_invalid_params() \
                .given_an_id() \
                .given_a_description() \
                .given_a_longitude() \
                .when_interactor_is_executed() \
                .then_permissions_should_be_validated() \
                .then_get_scene_should_be_called_with_id() \
                .then_scene_with_new_description_an_longitude_should_be_validated() \
                .then_update_scene_should_not_be_called() \
                .then_should_raise_invalid_entity_exception()

    def test_unexistent_scene_returns_entity_does_not_exist_error(self):
        TestModifyScene.ScenarioMaker() \
                .given_a_logged_person_id() \
                .given_a_permissions_validator_that_returns_true() \
                .given_an_scene_repo_that_raises_entity_does_not_exist() \
                .given_an_scene_validator_that_raises_invalid_params() \
                .given_an_id() \
                .given_a_description() \
                .given_a_longitude() \
                .when_interactor_is_executed() \
                .then_permissions_should_be_validated() \
                .then_get_scene_should_be_called_with_id() \
                .then_update_scene_should_not_be_called() \
                .then_should_raise_entity_does_not_exist()

    class ScenarioMaker:

        def given_a_logged_person_id(self):
            self.logged_person_id = '8'
            return self

        def given_a_permissions_validator_that_returns_true(self):
            self.permissions_validator = Mock()
            self.permissions_validator.validate_permissions.return_value = True
            return self

        def given_a_permissions_validator_that_raises_no_permissions_exception(self):
            self.permissions_validator = Mock()
            self.permissions_validator.validate_permissions.side_effect = NoPermissionException()
            return self

        def given_an_scene(self):
            self.scene = Scene(id='1', title='Title', description='some', latitude=1, longitude=0, experience_id=1)
            return self

        def given_an_scene_repo(self):
            self.scene_repo = Mock()
            return self

        def given_an_scene_repo_that_raises_entity_does_not_exist(self):
            self.scene_repo = Mock()
            self.scene_repo.get_scene.side_effect = EntityDoesNotExistException()
            return self

        def given_that_scene_repo_returns_that_scene_on_get(self):
            self.scene_repo.get_scene.return_value = self.scene
            return self

        def given_an_updated_scene(self):
            self.updated_scene = Scene(id='2', title='T', description='s', latitude=2, longitude=8, experience_id=1)
            return self

        def given_that_scene_repo_returns_that_scene_on_update(self):
            self.scene_repo.update_scene.return_value = self.updated_scene
            return self

        def given_an_scene_validator_that_accepts(self):
            self.scene_validator = Mock()
            self.scene_validator.validate_scene.return_value = True
            return self

        def given_an_scene_validator_that_raises_invalid_params(self):
            self.scene_validator = Mock()
            self.scene_validator.validate_scene.side_effect = InvalidEntityException(source='s', code='c', message='m')
            return self

        def given_an_id(self):
            self.id = '6'
            return self

        def given_a_description(self):
            self.description = 'description'
            return self

        def given_a_longitude(self):
            self.longitude = 0
            return self

        def when_interactor_is_executed(self):
            try:
                self.result = ModifySceneInteractor(self.scene_repo, self.scene_validator, self.permissions_validator) \
                    .set_params(id=self.id, title=None, description=self.description, latitude=None,
                                longitude=self.longitude, experience_id=1,
                                logged_person_id=self.logged_person_id).execute()
            except Exception as e:
                self.error = e
            return self

        def then_permissions_should_be_validated(self):
            self.permissions_validator.validate_permissions \
                    .assert_called_once_with(logged_person_id=self.logged_person_id,
                                             has_permissions_to_modify_experience=1)
            return self

        def then_get_scene_should_be_called_with_id(self):
            self.scene_repo.get_scene.assert_called_once_with(id=self.id)
            return self

        def then_scene_with_new_description_an_longitude_should_be_validated(self):
            new_scene = Scene(id=self.scene.id, title=self.scene.title, description=self.description,
                              latitude=self.scene.latitude, longitude=self.longitude,
                              experience_id=self.scene.experience_id)
            self.scene_validator.validate_scene.assert_called_once_with(new_scene)
            return self

        def then_update_scene_should_be_called_with_new_description_an_longitude(self):
            new_scene = Scene(id=self.scene.id, title=self.scene.title, description=self.description,
                              latitude=self.scene.latitude, longitude=self.longitude,
                              experience_id=self.scene.experience_id)
            self.scene_repo.update_scene.assert_called_once_with(new_scene)
            return self

        def then_result_should_be_updated_scene(self):
            assert self.result == self.updated_scene
            return self

        def then_update_scene_should_not_be_called(self):
            self.scene_repo.update_scene.assert_not_called()
            return self

        def then_should_raise_invalid_entity_exception(self):
            assert type(self.error) is InvalidEntityException
            assert self.error.source == 's'
            assert self.error.code == 'c'
            assert str(self.error) == 'm'
            return self

        def then_should_raise_entity_does_not_exist(self):
            assert type(self.error) is EntityDoesNotExistException
            return self


class TestUploadScenePictureInteractor:

    def test_validates_permissions_and_attach_picture_to_scene(self):
        TestUploadScenePictureInteractor.ScenarioMaker() \
                .given_a_logged_person_id() \
                .given_a_permissions_validator_that_returns_true() \
                .given_an_scene() \
                .given_an_scene_repo_that_returns_that_scene_on_attach() \
                .given_an_scene_id() \
                .given_a_picture() \
                .when_interactor_is_executed() \
                .then_should_validate_permissions() \
                .then_should_call_repo_attach_picture_to_scene() \
                .then_should_return_scene()

    def test_invalid_permissions_doesnt_attach_picture(self):
        TestUploadScenePictureInteractor.ScenarioMaker() \
                .given_a_logged_person_id() \
                .given_a_permissions_validator_that_raises_no_permissions_exception() \
                .given_an_scene_repo() \
                .given_an_scene_id() \
                .given_a_picture() \
                .when_interactor_is_executed() \
                .then_should_validate_permissions() \
                .then_should_not_call_repo_attach_picture_to_scene() \
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

        def given_an_scene(self):
            self.scene = Scene(id='2', title='T', description='s', latitude=2, longitude=8, experience_id=1)
            return self

        def given_an_scene_repo_that_returns_that_scene_on_attach(self):
            self.scene_repo = Mock()
            self.scene_repo.attach_picture_to_scene.return_value = self.scene
            return self

        def given_an_scene_repo(self):
            self.scene_repo = Mock()
            return self

        def given_an_scene_id(self):
            self.scene_id = '5'
            return self

        def given_a_picture(self):
            self.picture = 'pic'
            return self

        def when_interactor_is_executed(self):
            try:
                interactor = UploadScenePictureInteractor(scene_repo=self.scene_repo,
                                                          permissions_validator=self.permissions_validator)
                self.result = interactor.set_params(scene_id=self.scene_id, picture=self.picture,
                                                    logged_person_id=self.logged_person_id).execute()
            except Exception as e:
                self.error = e
            return self

        def then_should_validate_permissions(self):
            self.permissions_validator.validate_permissions \
                    .assert_called_once_with(logged_person_id=self.logged_person_id,
                                             has_permissions_to_modify_scene=self.scene_id)
            return self

        def then_should_call_repo_attach_picture_to_scene(self):
            self.scene_repo.attach_picture_to_scene.assert_called_once_with(scene_id=self.scene_id,
                                                                            picture=self.picture)
            return self

        def then_should_return_scene(self):
            assert self.result == self.scene
            return self

        def then_should_not_call_repo_attach_picture_to_scene(self):
            self.scene_repo.attach_picture_to_scene.assert_not_called()
            return self

        def then_should_raise_no_permissions_exception(self):
            assert type(self.error) is NoPermissionException
            return self


class TestIndexExperiencesInteractor:

    def test_indexes_existent_with_their_scenes_and_deletes_others(self):
        TestIndexExperiencesInteractor.ScenarioMaker() \
                .given_an_experience(id='2') \
                .given_an_scene(id='5', experience_id='2') \
                .given_an_scene(id='6', experience_id='2') \
                .given_an_experience(id='3') \
                .given_an_scene(id='7', experience_id='3') \
                .given_an_scene(id='8', experience_id='3') \
                .given_an_experience(id='4') \
                .given_an_experience_repo_that_returns_them() \
                .when_index(from_id='1', to_id='10') \
                .should_call_get_experiences_and_their_scenes() \
                .should_index_experiences_and_their_scenes() \
                .should_delete_experiences([1, 4, 5, 6, 7, 8, 9, 10])

    class ScenarioMaker:

        def __init__(self):
            self.search_repo = Mock()
            self.experiences = []
            self.scenes = []

        def given_an_experience(self, id):
            self.experiences.append(Experience(id=id, title='', description='', author_id='0'))
            return self

        def given_an_scene(self, id, experience_id):
            self.scenes.append(Scene(id=id, title='', description='',
                                     latitude=0, longitude=0, experience_id=experience_id))
            return self

        def given_an_experience_repo_that_returns_them(self):

            def fake_get_experience(id):
                experiences = [x for x in self.experiences if x.id == id]
                if len(experiences) > 0:
                    return experiences[0]
                else:
                    raise EntityDoesNotExistException
            self.repo = Mock()
            self.repo.get_experience.side_effect = fake_get_experience

            def fake_get_scenes(experience_id):
                return [x for x in self.scenes if x.experience_id == experience_id]
            self.scene_repo = Mock()
            self.scene_repo.get_scenes.side_effect = fake_get_scenes

            return self

        def when_index(self, from_id, to_id):
            interactor = IndexExperiencesInteractor(self.repo, self.search_repo, self.scene_repo)
            self.result = interactor.set_params(from_id, to_id).execute()
            return self

        def should_call_get_experiences_and_their_scenes(self):
            assert self.repo.get_experience.mock_calls == [call(str(i)) for i in range(1, 11)]
            assert self.scene_repo.get_scenes.mock_calls == [call('2'), call('3'), call('4')]
            return self

        def should_index_experiences_and_their_scenes(self):
            assert self.search_repo.index_experience_and_its_scenes.mock_calls == \
                [call(self.experiences[0], [self.scenes[0], self.scenes[1]]),
                 call(self.experiences[1], [self.scenes[2], self.scenes[3]])]
            return self

        def should_delete_experiences(self, experience_indexes):
            assert self.search_repo.delete_experience.mock_calls == \
                    [call(str(index)) for index in experience_indexes]
            return self
