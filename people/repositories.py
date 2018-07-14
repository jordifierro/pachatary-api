from pachatary.exceptions import EntityDoesNotExistException
from .models import ORMPerson, ORMAuthToken, ORMConfirmationToken, ORMLoginToken
from .entities import Person, AuthToken


class PersonRepo:

    def get_person(self, id=None, email=None):
        try:
            if id is not None:
                return self._decode_db_person(ORMPerson.objects.get(id=id))
            else:
                return self._decode_db_person(ORMPerson.objects.get(email=email))

        except ORMPerson.DoesNotExist:
            raise EntityDoesNotExistException

    def create_guest_person(self):
        created_orm_person = ORMPerson.objects.create()
        return self._decode_db_person(created_orm_person)

    def update_person(self, person):
        orm_person = ORMPerson.objects.get(id=person.id)

        orm_person.email = person.email
        orm_person.is_email_confirmed = person.is_email_confirmed

        orm_person.save()

        return self._decode_db_person(orm_person)

    def _decode_db_person(self, db_person):
        return Person(id=str(db_person.id), email=db_person.email,
                      is_email_confirmed=db_person.is_email_confirmed)


class AuthTokenRepo:

    def create_auth_token(self, person_id):
        created_orm_auth_token = ORMAuthToken.objects.create(person_id=person_id)
        return self._decode_db_auth_token(created_orm_auth_token)

    def get_auth_token(self, access_token=None, person_id=None):
        try:
            if access_token is not None:
                orm_auth_token = ORMAuthToken.objects.get(access_token=access_token)
            else:
                orm_auth_token = ORMAuthToken.objects.get(person_id=person_id)
            return self._decode_db_auth_token(orm_auth_token)
        except ORMAuthToken.DoesNotExist:
            raise EntityDoesNotExistException

    def _decode_db_auth_token(self, db_auth_token):
        return AuthToken(person_id=str(db_auth_token.person_id),
                         access_token=str(db_auth_token.access_token),
                         refresh_token=str(db_auth_token.refresh_token))


class ConfirmationTokenRepo:

    def get_person_id(self, confirmation_token):
        try:
            return str(ORMConfirmationToken.objects.get(token=confirmation_token).person_id)
        except ORMConfirmationToken.DoesNotExist:
            raise EntityDoesNotExistException

    def create_confirmation_token(self, person_id):
        created_orm_confirmation_token = ORMConfirmationToken.objects.create(person_id=person_id)
        return str(created_orm_confirmation_token.token)

    def delete_confirmation_tokens(self, person_id):
        ORMConfirmationToken.objects.filter(person_id=person_id).delete()
        return True


class LoginTokenRepo:

    def get_person_id(self, login_token):
        try:
            return str(ORMLoginToken.objects.get(token=login_token).person_id)
        except ORMLoginToken.DoesNotExist:
            raise EntityDoesNotExistException

    def create_login_token(self, person_id):
        created_orm_login_token = ORMLoginToken.objects.create(person_id=person_id)
        return str(created_orm_login_token.token)

    def delete_login_tokens(self, person_id):
        ORMLoginToken.objects.filter(person_id=person_id).delete()
        return True
