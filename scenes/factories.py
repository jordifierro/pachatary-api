from experiences.factories import ExperienceRepoFactory
from .repositories import SceneRepo
from .interactors import GetScenesFromExperienceInteractor, CreateNewSceneInteractor, ModifySceneInteractor
from .validators import SceneValidator
from .views import ScenesView, SceneView


class SceneRepoFactory(object):

    @staticmethod
    def create():
        return SceneRepo()


class SceneValidatorFactory(object):

    @staticmethod
    def create():
        experience_repo = ExperienceRepoFactory.create()
        return SceneValidator(experience_repo)


class GetScenesFromExperienceInteractorFactory(object):

    @staticmethod
    def create():
        scene_repo = SceneRepoFactory.create()
        return GetScenesFromExperienceInteractor(scene_repo=scene_repo)


class CreateNewSceneInteractorFactory(object):

    @staticmethod
    def create():
        scene_repo = SceneRepoFactory.create()
        scene_validator = SceneValidatorFactory.create()
        return CreateNewSceneInteractor(scene_repo=scene_repo, scene_validator=scene_validator)


class ModifySceneInteractorFactory(object):

    @staticmethod
    def create():
        scene_repo = SceneRepoFactory.create()
        scene_validator = SceneValidatorFactory.create()
        return ModifySceneInteractor(scene_repo=scene_repo, scene_validator=scene_validator)


class ScenesViewFactory(object):

    @staticmethod
    def create():
        get_scenes_from_experience_interactor = GetScenesFromExperienceInteractorFactory.create()
        create_new_scene_interactor = CreateNewSceneInteractorFactory.create()

        return ScenesView(get_scenes_from_experience_interactor=get_scenes_from_experience_interactor,
                          create_new_scene_interactor=create_new_scene_interactor)


class SceneViewFactory(object):

    @staticmethod
    def create():
        modify_scene_interactor = ModifySceneInteractorFactory.create()

        return SceneView(modify_scene_interactor=modify_scene_interactor)
