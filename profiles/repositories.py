from pachatary.exceptions import EntityDoesNotExistException
from pachatary.entities import Picture
from .models import ORMProfile
from .entities import Profile


class ProfileRepo:

    def get_profile(self, logged_person_id, person_id=None, username=None):
        try:
            if person_id is not None:
                return self._decode_db_profile(ORMProfile.objects.get(person_id=person_id), logged_person_id)
            elif username is not None:
                return self._decode_db_profile(ORMProfile.objects.get(username=username), logged_person_id)

        except ORMProfile.DoesNotExist:
            raise EntityDoesNotExistException

    def create_profile(self, profile):
        created_orm_profile = ORMProfile.objects.create(person_id=profile.person_id,
                                                        username=profile.username, bio=profile.bio)
        return self._decode_db_profile(created_orm_profile, str(created_orm_profile.person_id))

    def update_profile(self, profile):
        orm_profile = ORMProfile.objects.get(person_id=profile.person_id)

        orm_profile.username = profile.username
        orm_profile.bio = profile.bio

        orm_profile.save()

        return self._decode_db_profile(orm_profile, str(orm_profile.person_id))

    def attach_picture_to_profile(self, person_id, picture):
        profile = ORMProfile.objects.get(person_id=person_id)
        profile.picture = picture
        profile.save()
        return self._decode_db_profile(profile, str(profile.person_id))

    def _decode_db_profile(self, db_profile, logged_person_id):
        if not db_profile.picture:
            picture = None
        else:
            picture = Picture(tiny_url=db_profile.picture.tiny.url,
                              small_url=db_profile.picture.small.url,
                              medium_url=db_profile.picture.medium.url)
        return Profile(person_id=str(db_profile.person_id), username=db_profile.username, bio=db_profile.bio,
                       picture=picture, is_me=(logged_person_id == str(db_profile.person_id)))
