from elasticsearch import Elasticsearch

from django.urls import reverse
from django.conf import settings

from people.factories import create_person_permissions_validator, create_person_repo
from .repositories import ExperienceRepo, ExperienceSearchRepo
from .validators import ExperienceValidator, ExperiencePermissionsValidator
from .interactors import GetExperiencesInteractor, CreateNewExperienceInteractor, \
        ModifyExperienceInteractor, UploadExperiencePictureInteractor, SaveUnsaveExperienceInteractor, \
        SearchExperiencesInteractor, GetOrCreateExperienceShareIdInteractor, IdGenerator, \
        GetExperienceIdFromShareIdInteractor
from .views import ExperiencesView, ExperienceView, UploadExperiencePictureView, SaveExperienceView, \
        SearchExperiencesView, ExperienceShareUrlView, TranslateExperienceShareIdView


def create_experience_elastic_repo():
    elastic_client = Elasticsearch([settings.ELASTICSEARCH_URL])
    return ExperienceSearchRepo(elastic_client)


def create_experience_repo():
    return ExperienceRepo(search_repo=create_experience_elastic_repo())


def create_experience_validator():
    return ExperienceValidator()


def create_experience_permissions_validator():
    return ExperiencePermissionsValidator(experience_repo=create_experience_repo(),
                                          person_permissions_validator=create_person_permissions_validator())


def create_get_experiences_interactor():
    return GetExperiencesInteractor(experience_repo=create_experience_repo(), person_repo=create_person_repo(),
                                    permissions_validator=create_experience_permissions_validator())


def create_search_experiences_interactor():
    return SearchExperiencesInteractor(experience_repo=create_experience_repo(),
                                       permissions_validator=create_experience_permissions_validator())


def create_create_new_experience_interactor():
    return CreateNewExperienceInteractor(create_experience_repo(), create_experience_validator(),
                                         create_person_permissions_validator())


def create_modify_experience_interactor():
    return ModifyExperienceInteractor(experience_repo=create_experience_repo(),
                                      experience_validator=create_experience_validator(),
                                      permissions_validator=create_experience_permissions_validator())


def create_upload_experience_picture_interactor():
    return UploadExperiencePictureInteractor(experience_repo=create_experience_repo(),
                                             permissions_validator=create_experience_permissions_validator())


def create_save_unsave_experience_interactor():
    return SaveUnsaveExperienceInteractor(experience_repo=create_experience_repo(),
                                          permissions_validator=create_person_permissions_validator())


def create_id_generator():
    return IdGenerator()


def create_get_or_create_experience_share_id_interactor():
    return GetOrCreateExperienceShareIdInteractor(experience_repo=create_experience_repo(),
                                                  permissions_validator=create_person_permissions_validator(),
                                                  id_generator=create_id_generator())


def create_get_experience_id_from_share_id_interactor():
    return GetExperienceIdFromShareIdInteractor(experience_repo=create_experience_repo(),
                                                permissions_validator=create_person_permissions_validator())


def create_experiences_view(request, **kwargs):
    return ExperiencesView(get_experiences_interactor=create_get_experiences_interactor(),
                           get_experiences_base_url=request.build_absolute_uri(reverse('experiences')),
                           create_new_experience_interactor=create_create_new_experience_interactor())


def create_search_experiences_view(request, **kwargs):
    return SearchExperiencesView(search_experiences_interactor=create_search_experiences_interactor(),
                                 search_experiences_base_url=request.build_absolute_uri(reverse('search-experiences')))


def create_experience_view(request, **kwargs):
    return ExperienceView(modify_experience_interactor=create_modify_experience_interactor())


def create_upload_experience_picture_view(request, **kwargs):
    return UploadExperiencePictureView(
            upload_experience_picture_interactor=create_upload_experience_picture_interactor())


def create_save_experience_view(request, **kwargs):
    return SaveExperienceView(save_unsave_experience_interactor=create_save_unsave_experience_interactor())


def create_experience_share_url_view(request, **kwargs):
    return ExperienceShareUrlView(
        base_url=settings.PUBLIC_DOMAIN,
        get_or_create_experience_share_id_interactor=create_get_or_create_experience_share_id_interactor())


def create_translate_experience_share_id_view(request, **kwargs):
    return TranslateExperienceShareIdView(
            get_experience_id_from_share_id_interactor=create_get_experience_id_from_share_id_interactor())
