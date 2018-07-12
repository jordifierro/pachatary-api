from pachatary.decorators import serialize_exceptions
from .serializers import serialize_profile


class ProfileView:

    def __init__(self, get_profile_interactor=None, modify_profile_interactor=None):
        self.get_profile_interactor = get_profile_interactor
        self.modify_profile_interactor = modify_profile_interactor

    @serialize_exceptions
    def get(self, logged_person_id, username):
        profile = self.get_profile_interactor.set_params(logged_person_id=logged_person_id,
                                                         username=username).execute()
        body = serialize_profile(profile)
        status = 200
        return body, status

    @serialize_exceptions
    def patch(self, username=None, bio=None, logged_person_id=None):
        profile = self.modify_profile_interactor \
                .set_params(bio=bio, logged_person_id=logged_person_id).execute()

        body = serialize_profile(profile)
        status = 200
        return body, status


class UploadProfilePictureView:

    def __init__(self, upload_profile_picture_interactor=None):
        self.upload_profile_picture_interactor = upload_profile_picture_interactor

    @serialize_exceptions
    def post(self, picture, logged_person_id):
        profile = self.upload_profile_picture_interactor.set_params(picture=picture,
                                                                    logged_person_id=logged_person_id).execute()
        body = serialize_profile(profile)
        status = 200
        return body, status
