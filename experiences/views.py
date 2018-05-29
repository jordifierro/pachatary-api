from pachatary.decorators import serialize_exceptions
from .serializers import serialize_experiences_response, serialize_experience, serialize_experiences_search_response
from .interactors import SaveUnsaveExperienceInteractor


class ExperiencesView:

    def __init__(self, get_experiences_interactor=None,
                 get_experiences_base_url=None, create_new_experience_interactor=None):
        self.get_experiences_interactor = get_experiences_interactor
        self.get_experiences_base_url = get_experiences_base_url
        self.create_new_experience_interactor = create_new_experience_interactor

    @serialize_exceptions
    def get(self, username=None, saved=None, logged_person_id=None, limit='20', offset='0'):
        boolean_saved = (saved == 'true')
        limit = int(limit)
        offset = int(offset)

        experiences_result = self.get_experiences_interactor.set_params(username=username, saved=boolean_saved,
                                                                        logged_person_id=logged_person_id,
                                                                        limit=limit, offset=offset).execute()

        body = serialize_experiences_response(experiences=experiences_result['results'],
                                              base_url=self.get_experiences_base_url,
                                              username=username, saved=saved,
                                              next_limit=experiences_result['next_limit'],
                                              next_offset=experiences_result['next_offset'])

        status = 200
        return body, status

    @serialize_exceptions
    def post(self, title=None, description=None, logged_person_id=None):
        experience = self.create_new_experience_interactor \
                .set_params(title=title, description=description, logged_person_id=logged_person_id).execute()
        body = serialize_experience(experience)
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
        body = serialize_experience(experience)
        status = 200
        return body, status


class UploadExperiencePictureView:

    def __init__(self, upload_experience_picture_interactor=None):
        self.upload_experience_picture_interactor = upload_experience_picture_interactor

    @serialize_exceptions
    def post(self, picture, experience_id, logged_person_id):
        experience = self.upload_experience_picture_interactor.set_params(experience_id=experience_id, picture=picture,
                                                                          logged_person_id=logged_person_id).execute()
        body = serialize_experience(experience)
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


class SearchExperiencesView:

    def __init__(self, search_experiences_interactor=None, search_experiences_base_url=None):
        self.search_experiences_interactor = search_experiences_interactor
        self.search_experiences_base_url = search_experiences_base_url

    @serialize_exceptions
    def get(self, word=None, latitude=None, longitude=None, logged_person_id=None, limit='20', offset='0'):
        limit = int(limit)
        offset = int(offset)
        word = None if word == '' else word
        location = (float(latitude), float(longitude)) if latitude is not None and longitude is not None else None
        experiences_result = self.search_experiences_interactor.set_params(word=word, location=location,
                                                                           logged_person_id=logged_person_id,
                                                                           limit=limit, offset=offset).execute()
        body = serialize_experiences_search_response(experiences=experiences_result['results'],
                                                     base_url=self.search_experiences_base_url,
                                                     word=word, latitude=latitude, longitude=longitude,
                                                     next_limit=experiences_result['next_limit'],
                                                     next_offset=experiences_result['next_offset'])

        status = 200
        return body, status


class ExperienceShareUrlView:

    def __init__(self, base_url, get_or_create_experience_share_id_interactor):
        self.base_url = base_url
        self.get_or_create_experience_share_id_interactor = get_or_create_experience_share_id_interactor

    @serialize_exceptions
    def get(self, logged_person_id, experience_id):
        share_id = self.get_or_create_experience_share_id_interactor.set_params(logged_person_id=logged_person_id,
                                                                                experience_id=experience_id) \
                                                                                        .execute()
        body = {'share_url': '{}/e/{}'.format(self.base_url, share_id)}
        status = 200

        return body, status
