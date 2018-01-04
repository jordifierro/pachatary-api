import json

from django.conf import settings

from .repositories import PersonRepo, AuthTokenRepo
from .validators import ClientSecretKeyValidator, PersonValidator
from .interactors import CreateGuestPersonAndReturnAuthTokenInteractor
from .views import PeopleView


def create_person_repo():
    return PersonRepo()


def create_auth_token_repo():
    return AuthTokenRepo()


def create_client_secret_key_validator():
    return ClientSecretKeyValidator(valid_client_secret_key=settings.CLIENT_SECRET_KEY)


def create_guest_person_and_return_auth_token_interactor():
    return CreateGuestPersonAndReturnAuthTokenInteractor(
            client_secret_key_validator=create_client_secret_key_validator(),
            person_repo=create_person_repo(),
            auth_token_repo=create_auth_token_repo())


def create_people_view():
    return PeopleView(
            create_guest_person_and_return_auth_token_interactor=create_guest_person_and_return_auth_token_interactor())


def create_person_validator():
    project_name = settings.PROJECT_NAME

    generic_forbidden_usernames_json = open('/generic_forbidden_usernames.json')
    generic_forbidden_usernames = json.load(generic_forbidden_usernames_json)
    custom_forbidden_usernames_json = open('/custom_forbidden_usernames.json')
    custom_forbidden_usernames = json.load(custom_forbidden_usernames_json)
    forbidden_usernames = generic_forbidden_usernames + custom_forbidden_usernames

    forbidden_email_domains_json = open('/forbidden_email_domains.json')
    forbidden_email_domains = json.load(forbidden_email_domains_json)

    return PersonValidator(project_name=project_name, forbidden_usernames=forbidden_usernames,
                           forbidden_email_domains=forbidden_email_domains)
