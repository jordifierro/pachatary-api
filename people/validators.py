import re

from pachatary.exceptions import InvalidEntityException, NoLoggedException, NoPermissionException, \
        EntityDoesNotExistException


class ClientSecretKeyValidator:

    def __init__(self, valid_client_secret_key):
        self.valid_client_secret_key = valid_client_secret_key

    def validate(self, client_secret_key):
        if client_secret_key != self.valid_client_secret_key:
            raise InvalidEntityException(source='client_secret_key', code='invalid',
                                         message='Invalid client secret key')
        else:
            return True


class PersonValidator:

    def __init__(self, forbidden_email_domains, person_repo):
        self.forbidden_email_domains = forbidden_email_domains
        self.person_repo = person_repo

    def validate(self, person):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", person.email):
            raise InvalidEntityException(source='email', code='wrong', message='Email is wrong')
        if person.email.split('@')[-1] in self.forbidden_email_domains:
            raise InvalidEntityException(source='email', code='not_allowed', message='Email not allowed')
        try:
            same_email_person = self.person_repo.get_person(email=person.email)
            if same_email_person.id != person.id:
                raise InvalidEntityException(source='email', code='not_allowed', message='Email not allowed')
        except EntityDoesNotExistException:
            pass

        return True


class PersonPermissionsValidator:

    def __init__(self, person_repo):
        self.person_repo = person_repo

    def validate_permissions(self, logged_person_id, wants_to_create_content=False):
        if logged_person_id is None:
            raise NoLoggedException()

        if wants_to_create_content:
            if not self.person_repo.get_person(id=logged_person_id).is_email_confirmed:
                raise NoPermissionException()

        return True
