from people.factories import create_person_permissions_validator
from .repositories import ProfileRepo
from .interactors import GetProfileInteractor, ModifyProfileInteractor, \
        UploadProfilePictureInteractor
from .views import ProfileView, UploadProfilePictureView


def create_profile_repo():
    return ProfileRepo()


def create_get_profile_interactor():
    return GetProfileInteractor(profile_repo=create_profile_repo(),
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
