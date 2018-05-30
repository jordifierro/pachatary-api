import random
from enum import Enum

from pachatary.exceptions import ConflictException
from experiences.entities import Experience


class GetExperiencesInteractor:

    MAX_PAGINATE_LIMIT = 20

    def __init__(self, experience_repo, person_repo, permissions_validator):
        self.experience_repo = experience_repo
        self.person_repo = person_repo
        self.permissions_validator = permissions_validator

    def set_params(self, saved, username, logged_person_id, limit, offset):
        self.saved = saved
        self.username = username
        self.logged_person_id = logged_person_id
        self.limit = limit
        self.offset = offset
        return self

    def execute(self):
        self.permissions_validator.validate_permissions(logged_person_id=self.logged_person_id)

        if self.limit > GetExperiencesInteractor.MAX_PAGINATE_LIMIT:
            self.limit = GetExperiencesInteractor.MAX_PAGINATE_LIMIT

        if self.saved:
            result = self.experience_repo.get_saved_experiences(limit=self.limit, offset=self.offset,
                                                                logged_person_id=self.logged_person_id)
        else:
            if self.username == 'self':
                target_person_id = self.logged_person_id
            else:
                target_person_id = self.person_repo.get_person(username=self.username).id

            result = self.experience_repo.get_person_experiences(limit=self.limit, offset=self.offset,
                                                                 logged_person_id=self.logged_person_id,
                                                                 target_person_id=target_person_id)

        result.update({"next_limit": self.limit})
        return result


class SearchExperiencesInteractor:

    MAX_PAGINATION_LIMIT = 20

    def __init__(self, experience_repo, permissions_validator):
        self.experience_repo = experience_repo
        self.permissions_validator = permissions_validator

    def set_params(self, word, location, logged_person_id, limit, offset):
        self.word = word
        self.location = location
        self.logged_person_id = logged_person_id
        self.limit = limit
        self.offset = offset
        return self

    def execute(self):
        self.permissions_validator.validate_permissions(logged_person_id=self.logged_person_id)

        if self.limit > SearchExperiencesInteractor.MAX_PAGINATION_LIMIT:
            self.limit = SearchExperiencesInteractor.MAX_PAGINATION_LIMIT
        result = self.experience_repo.search_experiences(self.logged_person_id,
                                                         word=self.word, location=self.location,
                                                         limit=self.limit, offset=self.offset)
        result.update({"next_limit": self.limit})
        return result


class CreateNewExperienceInteractor:

    def __init__(self, experience_repo, experience_validator, permissions_validator):
        self.experience_repo = experience_repo
        self.experience_validator = experience_validator
        self.permissions_validator = permissions_validator

    def set_params(self, title, description, logged_person_id):
        self.title = title
        self.description = description
        self.logged_person_id = logged_person_id
        return self

    def execute(self):
        self.permissions_validator.validate_permissions(logged_person_id=self.logged_person_id,
                                                        wants_to_create_content=True)
        experience = Experience(title=self.title, description=self.description, author_id=self.logged_person_id)
        self.experience_validator.validate_experience(experience)
        return self.experience_repo.create_experience(experience)


class ModifyExperienceInteractor:

    def __init__(self, experience_repo, experience_validator, permissions_validator):
        self.experience_repo = experience_repo
        self.experience_validator = experience_validator
        self.permissions_validator = permissions_validator

    def set_params(self, id, title, description, logged_person_id):
        self.id = id
        self.title = title
        self.description = description
        self.logged_person_id = logged_person_id
        return self

    def execute(self):
        self.permissions_validator.validate_permissions(logged_person_id=self.logged_person_id,
                                                        has_permissions_to_modify_experience=self.id)
        experience = self.experience_repo.get_experience(id=self.id, logged_person_id=self.logged_person_id)

        new_title = self.title if self.title is not None else experience.title
        new_description = self.description if self.description is not None else experience.description
        updated_experience = experience.builder().title(new_title).description(new_description).build()

        self.experience_validator.validate_experience(updated_experience)

        return self.experience_repo.update_experience(updated_experience, logged_person_id=self.logged_person_id)


class UploadExperiencePictureInteractor:

    def __init__(self, experience_repo, permissions_validator):
        self.experience_repo = experience_repo
        self.permissions_validator = permissions_validator

    def set_params(self, experience_id, picture, logged_person_id):
        self.experience_id = experience_id
        self.picture = picture
        self.logged_person_id = logged_person_id
        return self

    def execute(self):
        self.permissions_validator.validate_permissions(logged_person_id=self.logged_person_id,
                                                        has_permissions_to_modify_experience=self.experience_id)
        return self.experience_repo.attach_picture_to_experience(experience_id=self.experience_id, picture=self.picture)


class SaveUnsaveExperienceInteractor:

    class Action(Enum):
        SAVE = 1
        UNSAVE = 2

    def __init__(self, experience_repo, permissions_validator):
        self.experience_repo = experience_repo
        self.permissions_validator = permissions_validator

    def set_params(self, action, experience_id, logged_person_id):
        self.action = action
        self.experience_id = experience_id
        self.logged_person_id = logged_person_id
        return self

    def execute(self):
        self.permissions_validator.validate_permissions(logged_person_id=self.logged_person_id)

        experience = self.experience_repo.get_experience(id=self.experience_id)
        if experience.author_id == self.logged_person_id:
            raise ConflictException(source='experience', code='self_save',
                                    message='You cannot save your own experiences')

        if self.action is SaveUnsaveExperienceInteractor.Action.SAVE:
            self.experience_repo.save_experience(person_id=self.logged_person_id, experience_id=self.experience_id)
        elif self.action is SaveUnsaveExperienceInteractor.Action.UNSAVE:
            self.experience_repo.unsave_experience(person_id=self.logged_person_id, experience_id=self.experience_id)

        return True


class GetOrCreateExperienceShareIdInteractor:

    def __init__(self, experience_repo, permissions_validator, id_generator):
        self.experience_repo = experience_repo
        self.permissions_validator = permissions_validator
        self.id_generator = id_generator

    def set_params(self, experience_id, logged_person_id):
        self.experience_id = experience_id
        self.logged_person_id = logged_person_id
        return self

    def execute(self):
        self.permissions_validator.validate_permissions(logged_person_id=self.logged_person_id)

        experience = self.experience_repo.get_experience(id=self.experience_id)
        if experience.share_id is not None:
            return experience.share_id

        updated_with_share_id = False
        while not updated_with_share_id:
            try:
                share_id = self.id_generator.generate()
                experience = experience.builder().share_id(share_id).build()
                experience = self.experience_repo.update_experience(experience)
                updated_with_share_id = True
            except ConflictException:
                pass

        return experience.share_id


class IdGenerator:

    LENGTH = 8
    CHOICES = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'

    def generate(self):
        return ''.join(random.choice(IdGenerator.CHOICES) for _ in range(IdGenerator.LENGTH))


class GetExperienceIdFromShareIdInteractor:

    def __init__(self, experience_repo, permissions_validator):
        self.experience_repo = experience_repo
        self.permissions_validator = permissions_validator

    def set_params(self, experience_share_id, logged_person_id):
        self.experience_share_id = experience_share_id
        self.logged_person_id = logged_person_id
        return self

    def execute(self):
        self.permissions_validator.validate_permissions(logged_person_id=self.logged_person_id)

        return self.experience_repo.get_experience(share_id=self.experience_share_id).id
