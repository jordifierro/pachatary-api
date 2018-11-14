from pachatary.exceptions import InvalidEntityException, BlockedContentException


class GetProfileInteractor:

    def __init__(self, profile_repo, block_repo, permissions_validator):
        self.profile_repo = profile_repo
        self.block_repo = block_repo
        self.permissions_validator = permissions_validator

    def set_params(self, username, logged_person_id):
        self.username = username
        self.logged_person_id = logged_person_id
        return self

    def execute(self):
        self.permissions_validator.validate_permissions(logged_person_id=self.logged_person_id)

        if self.username == 'self':
            return self.profile_repo.get_profile(person_id=self.logged_person_id,
                                                 logged_person_id=self.logged_person_id)
        else:
            profile = self.profile_repo.get_profile(username=self.username, logged_person_id=self.logged_person_id)
            if self.block_repo.block_exists(creator_id=self.logged_person_id, target_id=profile.person_id):
                raise BlockedContentException
            else:
                return profile


class ModifyProfileInteractor:

    MAX_BIO_LENGTH = 140

    def __init__(self, profile_repo, permissions_validator):
        self.profile_repo = profile_repo
        self.permissions_validator = permissions_validator

    def set_params(self, bio, logged_person_id):
        self.bio = bio
        self.logged_person_id = logged_person_id
        return self

    def execute(self):
        self.permissions_validator.validate_permissions(logged_person_id=self.logged_person_id)

        profile = self.profile_repo.get_profile(person_id=self.logged_person_id,
                                                logged_person_id=self.logged_person_id)

        if len(self.bio) > ModifyProfileInteractor.MAX_BIO_LENGTH:
            raise InvalidEntityException(source='bio', code='wrong_size',
                                         message='Bio can not be longer than 140 chars')

        return self.profile_repo.update_profile(profile.builder().bio(self.bio).build())


class UploadProfilePictureInteractor:

    def __init__(self, profile_repo, permissions_validator):
        self.profile_repo = profile_repo
        self.permissions_validator = permissions_validator

    def set_params(self, picture, logged_person_id):
        self.picture = picture
        self.logged_person_id = logged_person_id
        return self

    def execute(self):
        self.permissions_validator.validate_permissions(logged_person_id=self.logged_person_id)
        return self.profile_repo.attach_picture_to_profile(person_id=self.logged_person_id, picture=self.picture)
