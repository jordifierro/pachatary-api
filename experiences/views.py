from pachatary.decorators import serialize_exceptions
from .serializers import ExperiencesResponseSerializer, ExperienceSerializer
from .interactors import SaveUnsaveExperienceInteractor


class ExperiencesView:

    def __init__(self, get_all_experiences_interactor=None, get_experiences_base_url=None,
                 create_new_experience_interactor=None):
        self.get_all_experiences_interactor = get_all_experiences_interactor
        self.get_experiences_base_url = get_experiences_base_url
        self.create_new_experience_interactor = create_new_experience_interactor

    @serialize_exceptions
    def get(self, mine='false', saved='false', logged_person_id=None, limit='20', offset='0'):
        boolean_mine = (mine == 'true')
        boolean_saved = (saved == 'true')
        limit = int(limit)
        offset = int(offset)
        experiences_result = self.get_all_experiences_interactor.set_params(mine=boolean_mine, saved=boolean_saved,
                                                                            logged_person_id=logged_person_id,
                                                                            limit=limit, offset=offset).execute()

        body = ExperiencesResponseSerializer.serialize(experiences=experiences_result["results"],
                                                       base_url=self.get_experiences_base_url,
                                                       mine=mine, saved=saved,
                                                       next_limit=experiences_result['next_limit'],
                                                       next_offset=experiences_result['next_offset'])
        status = 200
        return body, status

    @serialize_exceptions
    def post(self, title=None, description=None, logged_person_id=None):
        experience = self.create_new_experience_interactor \
                .set_params(title=title, description=description, logged_person_id=logged_person_id).execute()
        body = ExperienceSerializer.serialize(experience)
        status = 201
        return body, status


class ExperienceView:

    def __init__(self, modify_experience_interactor=None):
        self.modify_experience_interactor = modify_experience_interactor

    @serialize_exceptions
    def patch(self, experience_id, title=None, description=None, logged_person_id=None):
        experience = self.modify_experience_interactor \
                .set_params(id=experience_id, title=title,
                            description=description, logged_person_id=logged_person_id).execute()
        body = ExperienceSerializer.serialize(experience)
        status = 200
        return body, status


class UploadExperiencePictureView:

    def __init__(self, upload_experience_picture_interactor=None):
        self.upload_experience_picture_interactor = upload_experience_picture_interactor

    @serialize_exceptions
    def post(self, picture, experience_id, logged_person_id):
        experience = self.upload_experience_picture_interactor.set_params(experience_id=experience_id, picture=picture,
                                                                          logged_person_id=logged_person_id).execute()
        body = ExperienceSerializer.serialize(experience)
        status = 200
        return body, status


class SaveExperienceView:

    def __init__(self, save_unsave_experience_interactor):
        self.save_unsave_experience_interactor = save_unsave_experience_interactor

    @serialize_exceptions
    def post(self, experience_id, logged_person_id):
        self.save_unsave_experience_interactor \
                .set_params(action=SaveUnsaveExperienceInteractor.Action.SAVE,
                            experience_id=experience_id, logged_person_id=logged_person_id).execute()
        body = ''
        status = 201
        return body, status

    @serialize_exceptions
    def delete(self, experience_id, logged_person_id):
        self.save_unsave_experience_interactor \
                .set_params(action=SaveUnsaveExperienceInteractor.Action.UNSAVE,
                            experience_id=experience_id, logged_person_id=logged_person_id).execute()
        body = None
        status = 204
        return body, status
