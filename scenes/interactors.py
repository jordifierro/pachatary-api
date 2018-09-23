from pachatary.exceptions import EntityDoesNotExistException
from .entities import Scene


class GetScenesFromExperienceInteractor:

    def __init__(self, scene_repo, permissions_validator):
        self.scene_repo = scene_repo
        self.permissions_validator = permissions_validator

    def set_params(self, experience_id, logged_person_id):
        self.experience_id = experience_id
        self.logged_person_id = logged_person_id
        return self

    def execute(self):
        self.permissions_validator.validate_permissions(logged_person_id=self.logged_person_id)
        scenes = self.scene_repo.get_scenes(experience_id=self.experience_id)
        scenes.sort(key=lambda x: x.id, reverse=False)
        return scenes


class CreateNewSceneInteractor:

    def __init__(self, scene_repo, scene_validator, permissions_validator, reindex_experience):
        self.scene_repo = scene_repo
        self.scene_validator = scene_validator
        self.permissions_validator = permissions_validator
        self.reindex_experience = reindex_experience

    def set_params(self, title, description, latitude, longitude, experience_id, logged_person_id):
        self.title = title
        self.description = description
        self.latitude = latitude
        self.longitude = longitude
        self.experience_id = experience_id
        self.logged_person_id = logged_person_id
        return self

    def execute(self):
        self.permissions_validator.validate_permissions(logged_person_id=self.logged_person_id,
                                                        has_permissions_to_modify_experience=self.experience_id)
        scene = Scene(title=self.title, description=self.description,
                      latitude=self.latitude, longitude=self.longitude, experience_id=self.experience_id)
        self.scene_validator.validate_scene(scene)
        created_scene = self.scene_repo.create_scene(scene)

        self.reindex_experience(self.experience_id)

        return created_scene


class ModifySceneInteractor:

    def __init__(self, scene_repo, scene_validator, permissions_validator):
        self.scene_repo = scene_repo
        self.scene_validator = scene_validator
        self.permissions_validator = permissions_validator

    def set_params(self, id, title, description, latitude, longitude, experience_id, logged_person_id):
        self.id = id
        self.title = title
        self.description = description
        self.latitude = latitude
        self.longitude = longitude
        self.experience_id = experience_id
        self.logged_person_id = logged_person_id
        return self

    def execute(self):
        self.permissions_validator.validate_permissions(logged_person_id=self.logged_person_id,
                                                        has_permissions_to_modify_experience=self.experience_id)

        scene = self.scene_repo.get_scene(id=self.id)

        new_title = self.title if self.title is not None else scene.title
        new_description = self.description if self.description is not None else scene.description
        new_latitude = self.latitude if self.latitude is not None else scene.latitude
        new_longitude = self.longitude if self.longitude is not None else scene.longitude
        new_experience_id = self.experience_id if self.experience_id is not None else scene.experience_id
        updated_scene = Scene(id=scene.id, title=new_title, description=new_description, latitude=new_latitude,
                              longitude=new_longitude, experience_id=new_experience_id)

        self.scene_validator.validate_scene(updated_scene)

        return self.scene_repo.update_scene(updated_scene)


class UploadScenePictureInteractor:

    def __init__(self, scene_repo, permissions_validator):
        self.scene_repo = scene_repo
        self.permissions_validator = permissions_validator

    def set_params(self, scene_id, picture, logged_person_id):
        self.scene_id = scene_id
        self.picture = picture
        self.logged_person_id = logged_person_id
        return self

    def execute(self):
        self.permissions_validator.validate_permissions(logged_person_id=self.logged_person_id,
                                                        has_permissions_to_modify_scene=self.scene_id)
        return self.scene_repo.attach_picture_to_scene(scene_id=self.scene_id, picture=self.picture)


class IndexExperiencesInteractor:

    def __init__(self, experience_repo, experience_search_repo, scene_repo):
        self.experience_repo = experience_repo
        self.experience_search_repo = experience_search_repo
        self.scene_repo = scene_repo

    def set_params(self, from_id, to_id):
        self.from_id = from_id
        self.to_id = to_id
        return self

    def execute(self):
        for i in range(int(self.from_id), int(self.to_id) + 1):
            try:
                experience = self.experience_repo.get_experience(str(i))
                scenes = self.scene_repo.get_scenes(str(i))
                if len(scenes) > 0:
                    self.experience_search_repo.index_experience_and_its_scenes(experience, scenes)
            except EntityDoesNotExistException:
                pass
