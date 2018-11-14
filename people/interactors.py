from pachatary.exceptions import EntityDoesNotExistException, ConflictException, NoLoggedException, \
        InvalidEntityException
from people.entities import Person
from profiles.entities import Profile
from experiences.interactors import SaveUnsaveExperienceInteractor


class CreateGuestPersonAndReturnAuthTokenInteractor:

    def __init__(self, client_secret_key_validator, person_repo, auth_token_repo):
        self.client_secret_key_validator = client_secret_key_validator
        self.person_repo = person_repo
        self.auth_token_repo = auth_token_repo

    def set_params(self, client_secret_key):
        self.client_secret_key = client_secret_key
        return self

    def execute(self):
        self.client_secret_key_validator.validate(client_secret_key=self.client_secret_key)

        created_guest_person = self.person_repo.create_guest_person()

        return self.auth_token_repo.create_auth_token(person_id=created_guest_person.id)


class AuthenticateInteractor:

    def __init__(self, auth_token_repo):
        self.auth_token_repo = auth_token_repo

    def set_params(self, access_token):
        self.access_token = access_token
        return self

    def execute(self):
        try:
            auth_token = self.auth_token_repo.get_auth_token(access_token=self.access_token)
            return str(auth_token.person_id)
        except EntityDoesNotExistException:
            return None


class RegisterUsernameAndEmailInteractor:

    def __init__(self, person_validator, person_repo, profile_validator, profile_repo,
                 confirmation_token_repo, mailer_service):
        self.person_validator = person_validator
        self.person_repo = person_repo
        self.profile_validator = profile_validator
        self.profile_repo = profile_repo
        self.confirmation_token_repo = confirmation_token_repo
        self.mailer_service = mailer_service

    def set_params(self, logged_person_id, username, email):
        self.logged_person_id = logged_person_id
        self.username = username
        self.email = email
        return self

    def execute(self):
        if self.logged_person_id is None:
            raise NoLoggedException()

        person = self.person_repo.get_person(id=self.logged_person_id)
        if person.is_email_confirmed:
            raise ConflictException(source='person', code='already_registered', message='Person already registered')

        updated_person = Person(id=person.id, email=self.email, is_email_confirmed=False)
        self.person_validator.validate(updated_person)
        try:
            profile = self.profile_repo.get_profile(person_id=self.logged_person_id,
                                                    logged_person_id=self.logged_person_id)
            updated_profile = profile.builder().username(self.username).build()

            self.profile_validator.validate(updated_profile)

            profile = self.profile_repo.update_profile(updated_profile)
        except EntityDoesNotExistException:
            new_profile = Profile(person_id=self.logged_person_id, username=self.username)

            self.profile_validator.validate(new_profile)

            profile = self.profile_repo.create_profile(new_profile)

        updated_person = self.person_repo.update_person(updated_person)

        self.confirmation_token_repo.delete_confirmation_tokens(person_id=self.logged_person_id)
        confirmation_token = self.confirmation_token_repo.create_confirmation_token(person_id=self.logged_person_id)
        self.mailer_service.send_ask_confirmation_mail(confirmation_token=confirmation_token,
                                                       username=self.username, email=self.email)
        return True


class ConfirmEmailInteractor:

    def __init__(self, person_repo, confirmation_token_repo):
        self.person_repo = person_repo
        self.confirmation_token_repo = confirmation_token_repo

    def set_params(self, logged_person_id, confirmation_token):
        self.logged_person_id = logged_person_id
        self.confirmation_token = confirmation_token
        return self

    def execute(self):
        if self.logged_person_id is None:
            raise NoLoggedException()

        try:
            person_id = self.confirmation_token_repo.get_person_id(confirmation_token=self.confirmation_token)
        except EntityDoesNotExistException:
            raise InvalidEntityException(source='confirmation_token', code='invalid',
                                         message='Invalid confirmation token')

        if person_id != self.logged_person_id:
            raise InvalidEntityException(source='confirmation_token', code='invalid',
                                         message='Invalid confirmation token')

        self.confirmation_token_repo.delete_confirmation_tokens(person_id=person_id)

        person = self.person_repo.get_person(id=self.logged_person_id)
        updated_person = Person(id=person.id, email=person.email, is_email_confirmed=True)
        self.person_repo.update_person(updated_person)

        return True


class LoginEmailInteractor:

    def __init__(self, person_repo, profile_repo, login_token_repo, mailer_service):
        self.person_repo = person_repo
        self.profile_repo = profile_repo
        self.login_token_repo = login_token_repo
        self.mailer_service = mailer_service

    def set_params(self, email):
        self.email = email
        return self

    def execute(self):
        try:
            person = self.person_repo.get_person(email=self.email)
            if not person.is_email_confirmed:
                return None
            profile = self.profile_repo.get_profile(person_id=person.id, logged_person_id=person.id)
        except EntityDoesNotExistException:
            return None

        self.login_token_repo.delete_login_tokens(person_id=person.id)
        login_token = self.login_token_repo.create_login_token(person_id=person.id)
        self.mailer_service.send_login_mail(login_token=login_token, username=profile.username, email=person.email)

        return None


class LoginInteractor:

    def __init__(self, person_repo, auth_token_repo, login_token_repo):
        self.person_repo = person_repo
        self.auth_token_repo = auth_token_repo
        self.login_token_repo = login_token_repo

    def set_params(self, login_token):
        self.login_token = login_token
        return self

    def execute(self):
        person_id = self.login_token_repo.get_person_id(login_token=self.login_token)
        self.login_token_repo.delete_login_tokens(person_id=person_id)
        auth_token = self.auth_token_repo.get_auth_token(person_id=person_id)
        return auth_token


class BlockInteractor:

    def __init__(self, permissions_validator, block_repo, experience_repo, save_unsave_experience_interactor):
        self.permissions_validator = permissions_validator
        self.block_repo = block_repo
        self.experience_repo = experience_repo
        self.save_unsave_experience_interactor = save_unsave_experience_interactor

    def set_params(self, logged_person_id, target_id):
        self.logged_person_id = logged_person_id
        self.target_id = target_id
        return self

    def execute(self):
        self.permissions_validator.validate_permissions(logged_person_id=self.logged_person_id)

        if self.block_repo.block_exists(creator_id=self.logged_person_id, target_id=self.target_id):
            return True

        saved_experiences = self.experience_repo.get_saved_experiences(logged_person_id=self.logged_person_id,
                                                                       offset=0, limit=1000000)['results']
        for experience in saved_experiences:
            if experience.author_id == self.target_id:
                self.save_unsave_experience_interactor.set_params(action=SaveUnsaveExperienceInteractor.Action.UNSAVE,
                                                                  experience_id=experience.id,
                                                                  logged_person_id=self.logged_person_id).execute()

        return self.block_repo.block(creator_id=self.logged_person_id, target_id=self.target_id)
