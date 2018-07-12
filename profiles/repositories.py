from pachatary.exceptions import EntityDoesNotExistException
from .models import ORMProfile
from .entities import Profile


class ProfileRepo:

    def get_profile(self, person_id=None, username=None):
        try:
            if person_id is not None:
                return self._decode_db_profile(ORMProfile.objects.get(person_id=person_id))
            elif username is not None:
                return self._decode_db_profile(ORMProfile.objects.get(username=username))

        except ORMProfile.DoesNotExist:
            raise EntityDoesNotExistException

    def create_profile(self, profile):
        created_orm_profile = ORMProfile.objects.create(person_id=profile.person_id,
                                                        username=profile.username, bio=profile.bio)
        return self._decode_db_profile(created_orm_profile)

    def update_profile(self, profile):
        orm_profile = ORMProfile.objects.get(person_id=profile.person_id)

        orm_profile.username = profile.username
        orm_profile.bio = profile.bio

        orm_profile.save()

        return self._decode_db_profile(orm_profile)

    def attach_picture_to_profile(self, person_id, picture):
        profile = ORMProfile.objects.get(person_id=person_id)
        profile.picture = picture
        profile.save()
        return self._decode_db_profile(profile)

    def _decode_db_profile(self, db_profile):
        return Profile(person_id=db_profile.person_id, username=db_profile.username, bio=db_profile.bio)
