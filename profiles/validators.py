import re

from pachatary.exceptions import InvalidEntityException, EntityDoesNotExistException


class ProfileValidator:

    USERNAME_MIN_LENGTH = 3
    USERNAME_MAX_LENGTH = 20
    BIO_MAX_LENGTH = 140
    USERNAME_REGEX = '(?!\.)(?!\_)(?!.*?\.\.)(?!.*?\.\_)(?!.*?\_\.)(?!.*?\_\_)(?!.*\.$)(?!.*\_$)[a-z0-9_.]+$'

    def __init__(self, project_name, forbidden_usernames, profile_repo):
        self.project_name = project_name
        self.forbidden_usernames = forbidden_usernames
        self.profile_repo = profile_repo

    def validate(self, profile):
        if len(profile.username) < ProfileValidator.USERNAME_MIN_LENGTH or \
                len(profile.username) > ProfileValidator.USERNAME_MAX_LENGTH:
            raise InvalidEntityException(source='username', code='wrong_size',
                                         message='Username length should be between 1 and 20 chars')
        if not re.match(ProfileValidator.USERNAME_REGEX, profile.username):
            raise InvalidEntityException(source='username', code='not_allowed', message='Username not allowed')
        if self.project_name in profile.username:
            raise InvalidEntityException(source='username', code='not_allowed', message='Username not allowed')
        if profile.username in self.forbidden_usernames:
            raise InvalidEntityException(source='username', code='not_allowed', message='Username not allowed')
        try:
            same_username_profile = self.profile_repo.get_profile(username=profile.username, logged_person_id='any')
            if same_username_profile.person_id != profile.person_id:
                raise InvalidEntityException(source='username', code='not_allowed', message='Username not allowed')
        except EntityDoesNotExistException:
            pass

        if len(profile.bio) > ProfileValidator.BIO_MAX_LENGTH:
            raise InvalidEntityException(source='bio', code='wrong_size',
                                         message='Bio length should not be more than 140 chars')

        return True
