import random
from enum import Enum

from pachatary.exceptions import ConflictException, BlockedContentException
from experiences.entities import Experience


class GetExperiencesInteractor:

    MAX_PAGINATE_LIMIT = 20

    def __init__(self, experience_repo, get_profile_interactor, permissions_validator):
        self.experience_repo = experience_repo
        self.get_profile_interactor = get_profile_interactor
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
                target_person_id = self.get_profile_interactor.set_params(
                        username=self.username, logged_person_id=self.logged_person_id).execute().person_id

            result = self.experience_repo.get_person_experiences(limit=self.limit, offset=self.offset,
                                                                 logged_person_id=self.logged_person_id,
                                                                 target_person_id=target_person_id)

        result.update({"next_limit": self.limit})
        return result


class SearchExperiencesInteractor:

    MAX_PAGINATION_LIMIT = 20

    def __init__(self, experience_repo, block_repo, permissions_validator):
        self.experience_repo = experience_repo
        self.block_repo = block_repo
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

        blocked_people = self.block_repo.get_blocked_people(person_id=self.logged_person_id)
        if len(blocked_people) > 0:
            filtered_experiences = [x for x in result['results'] if x.author_id not in blocked_people]
            result.update({'results': filtered_experiences})

        result.update({'next_limit': self.limit})
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

    def __init__(self, experience_repo, permissions_validator, get_experience_interactor):
        self.experience_repo = experience_repo
        self.permissions_validator = permissions_validator
        self.get_experience_interactor = get_experience_interactor

    def set_params(self, action, experience_id, logged_person_id):
        self.action = action
        self.experience_id = experience_id
        self.logged_person_id = logged_person_id
        return self

    def execute(self):
        self.permissions_validator.validate_permissions(logged_person_id=self.logged_person_id)

        experience = self.get_experience_interactor.set_params(experience_id=self.experience_id,
                                                               logged_person_id=self.logged_person_id).execute()
        if experience.author_id == self.logged_person_id:
            raise ConflictException(source='experience', code='self_save',
                                    message='You cannot save your own experiences')

        if self.action is SaveUnsaveExperienceInteractor.Action.SAVE:
            self.experience_repo.save_experience(person_id=self.logged_person_id, experience_id=self.experience_id)
        elif self.action is SaveUnsaveExperienceInteractor.Action.UNSAVE:
            self.experience_repo.unsave_experience(person_id=self.logged_person_id, experience_id=self.experience_id)

        return True


class GetOrCreateExperienceShareIdInteractor:

    def __init__(self, experience_repo, permissions_validator, id_generator, get_experience_interactor):
        self.experience_repo = experience_repo
        self.permissions_validator = permissions_validator
        self.id_generator = id_generator
        self.get_experience_interactor = get_experience_interactor

    def set_params(self, experience_id, logged_person_id):
        self.experience_id = experience_id
        self.logged_person_id = logged_person_id
        return self

    def execute(self):
        self.permissions_validator.validate_permissions(logged_person_id=self.logged_person_id)

        experience = self.get_experience_interactor.set_params(experience_id=self.experience_id,
                                                               logged_person_id=self.logged_person_id).execute()
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


class GetExperienceInteractor:

    def __init__(self, experience_repo, block_repo, permissions_validator):
        self.experience_repo = experience_repo
        self.block_repo = block_repo
        self.permissions_validator = permissions_validator

    def set_params(self, experience_id=None, experience_share_id=None, logged_person_id=None):
        self.experience_id = experience_id
        self.experience_share_id = experience_share_id
        self.logged_person_id = logged_person_id
        return self

    def execute(self):
        self.permissions_validator.validate_permissions(logged_person_id=self.logged_person_id)

        if self.experience_id is not None:
            experience = self.experience_repo.get_experience(id=self.experience_id,
                                                             logged_person_id=self.logged_person_id)
        elif self.experience_share_id is not None:
            experience = self.experience_repo.get_experience(share_id=self.experience_share_id,
                                                             logged_person_id=self.logged_person_id)

        if self.block_repo.block_exists(creator_id=self.logged_person_id, target_id=experience.author_id):
            raise BlockedContentException
        else:
            return experience


class FlagExperienceInteractor:

    def __init__(self, experience_repo, permissions_validator, get_experience_interactor):
        self.experience_repo = experience_repo
        self.permissions_validator = permissions_validator
        self.get_experience_interactor = get_experience_interactor

    def set_params(self, logged_person_id, experience_id, reason):
        self.logged_person_id = logged_person_id
        self.experience_id = experience_id
        self.reason = reason
        return self

    def execute(self):
        self.permissions_validator.validate_permissions(logged_person_id=self.logged_person_id)

        self.get_experience_interactor.set_params(experience_id=self.experience_id,
                                                  logged_person_id=self.logged_person_id).execute()

        return self.experience_repo.flag_experience(person_id=self.logged_person_id,
                                                    experience_id=self.experience_id,
                                                    reason=self.reason)
