import json

from django.conf import settings

from profiles.factories import create_profile_repo, create_profile_validator
from .basic_factories import create_person_repo
from .repositories import AuthTokenRepo, ConfirmationTokenRepo, LoginTokenRepo
from .validators import ClientSecretKeyValidator, PersonValidator
from .interactors import CreateGuestPersonAndReturnAuthTokenInteractor, RegisterUsernameAndEmailInteractor, \
        AuthenticateInteractor, ConfirmEmailInteractor, LoginEmailInteractor, LoginInteractor
from .views import PeopleView, PersonView, EmailConfirmationView, LoginEmailView, LoginView
from .services import MailerService


def create_auth_token_repo():
    return AuthTokenRepo()


def create_confirmation_token_repo():
    return ConfirmationTokenRepo()


def create_login_token_repo():
    return LoginTokenRepo()


def create_client_secret_key_validator():
    return ClientSecretKeyValidator(valid_client_secret_key=settings.CLIENT_SECRET_KEY)


def create_person_validator():
    forbidden_email_domains_json = open('people/forbidden_email_domains.json')
    forbidden_email_domains = json.load(forbidden_email_domains_json)

    person_repo = create_person_repo()

    return PersonValidator(forbidden_email_domains=forbidden_email_domains, person_repo=person_repo)


def create_mailer_service():
    return MailerService()


def create_authenticate_interactor():
    return AuthenticateInteractor(auth_token_repo=create_auth_token_repo())


def create_guest_person_and_return_auth_token_interactor():
    return CreateGuestPersonAndReturnAuthTokenInteractor(
            client_secret_key_validator=create_client_secret_key_validator(),
            person_repo=create_person_repo(),
            auth_token_repo=create_auth_token_repo())


def create_register_username_and_email_interactor():
    person_validator = create_person_validator()
    person_repo = create_person_repo()
    profile_validator = create_profile_validator()
    profile_repo = create_profile_repo()
    confirmation_token_repo = create_confirmation_token_repo()
    mailer_service = create_mailer_service()
    return RegisterUsernameAndEmailInteractor(person_validator=person_validator, person_repo=person_repo,
                                              profile_validator=profile_validator, profile_repo=profile_repo,
                                              confirmation_token_repo=confirmation_token_repo,
                                              mailer_service=mailer_service)


def create_confirm_email_interactor():
    return ConfirmEmailInteractor(confirmation_token_repo=create_confirmation_token_repo(),
                                  person_repo=create_person_repo())


def create_login_email_interactor():
    return LoginEmailInteractor(person_repo=create_person_repo(), login_token_repo=create_login_token_repo(),
                                mailer_service=create_mailer_service())


def create_login_interactor():
    return LoginInteractor(person_repo=create_person_repo(), auth_token_repo=create_auth_token_repo(),
                           login_token_repo=create_login_token_repo())


def create_people_view(request, **kwargs):
    return PeopleView(
            create_guest_person_and_return_auth_token_interactor=create_guest_person_and_return_auth_token_interactor())


def create_person_view(request, **kwargs):
    return PersonView(register_username_and_email_interactor=create_register_username_and_email_interactor())


def create_email_confirmation_view(request, **kwargs):
    return EmailConfirmationView(confirm_email_interactor=create_confirm_email_interactor())


def create_login_email_view(request, **kwargs):
    return LoginEmailView(login_email_interactor=create_login_email_interactor())


def create_login_view(request, **kwargs):
    return LoginView(login_interactor=create_login_interactor())
