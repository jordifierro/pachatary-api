import json

from django.conf import settings

from people.basic_factories import create_person_permissions_validator, create_block_repo
from .repositories import ProfileRepo
from .interactors import GetProfileInteractor, ModifyProfileInteractor, \
        UploadProfilePictureInteractor
from .views import ProfileView, UploadProfilePictureView
from .validators import ProfileValidator


def create_profile_repo():
    return ProfileRepo()


def create_profile_validator():
    project_name = settings.PROJECT_NAME

    generic_forbidden_usernames_json = open('profiles/generic_forbidden_usernames.json')
    generic_forbidden_usernames = json.load(generic_forbidden_usernames_json)
    custom_forbidden_usernames_json = open('profiles/custom_forbidden_usernames.json')
    custom_forbidden_usernames = json.load(custom_forbidden_usernames_json)
    forbidden_usernames = generic_forbidden_usernames + custom_forbidden_usernames

    profile_repo = create_profile_repo()

    return ProfileValidator(project_name=project_name, forbidden_usernames=forbidden_usernames,
                            profile_repo=profile_repo)


def create_get_profile_interactor():
    return GetProfileInteractor(profile_repo=create_profile_repo(), block_repo=create_block_repo(),
                                permissions_validator=create_person_permissions_validator())


def create_modify_profile_interactor():
    return ModifyProfileInteractor(profile_repo=create_profile_repo(),
                                   permissions_validator=create_person_permissions_validator())


def create_upload_profile_picture_interactor():
    return UploadProfilePictureInteractor(profile_repo=create_profile_repo(),
                                          permissions_validator=create_person_permissions_validator())


def create_profile_view(request, **kwargs):
    return ProfileView(get_profile_interactor=create_get_profile_interactor(),
                       modify_profile_interactor=create_modify_profile_interactor())


def create_upload_profile_picture_view(request, **kwargs):
    return UploadProfilePictureView(
            upload_profile_picture_interactor=create_upload_profile_picture_interactor())
