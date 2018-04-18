from pachatary.entities import Picture
from pachatary.exceptions import EntityDoesNotExistException
from .models import ORMExperience, ORMSave
from .entities import Experience


class ExperienceRepo:

    def _decode_db_experience(self, db_experience, is_mine=False, is_saved=False):
        if not db_experience.picture:
            picture = None
        else:
            picture = Picture(small_url=db_experience.picture.small.url,
                              medium_url=db_experience.picture.medium.url,
                              large_url=db_experience.picture.large.url)

        return Experience(id=db_experience.id,
                          title=db_experience.title,
                          description=db_experience.description,
                          picture=picture,
                          author_id=db_experience.author.id,
                          author_username=db_experience.author.username,
                          is_mine=is_mine,
                          is_saved=is_saved)

    def get_all_experiences(self, logged_person_id, offset=0, limit=100, mine=False, saved=False):
        if saved:
            db_experiences = \
                [save.experience for save
                    in ORMSave.objects.order_by('-id').select_related('experience').filter(person_id=logged_person_id)]
        else:
            all_db_experiences = ORMExperience.objects.order_by('-id').select_related('author').all()
            if mine:
                db_experiences = all_db_experiences.filter(author_id=logged_person_id)
            else:
                saved_experience_ids = ORMSave.objects.values('experience_id').filter(person_id=logged_person_id)
                db_experiences = all_db_experiences.exclude(author_id=logged_person_id) \
                                                   .exclude(id__in=saved_experience_ids)

        paginated_db_experiences = db_experiences[offset:offset+limit+1]
        next_offset = None
        if len(paginated_db_experiences) == limit+1:
            next_offset = offset + limit

        experiences = []
        for db_experience in paginated_db_experiences[0:limit]:
            experiences.append(self._decode_db_experience(db_experience, mine, saved))
        return {"results": experiences, "next_offset": next_offset}

    def get_experience(self, id, logged_person_id=None):
        try:
            db_experience = ORMExperience.objects.select_related('author').get(id=id)
            return self._decode_db_experience(db_experience, is_mine=(logged_person_id == db_experience.author_id))
        except ORMExperience.DoesNotExist:
            raise EntityDoesNotExistException()

    def create_experience(self, experience):
        db_experience = ORMExperience.objects.create(title=experience.title,
                                                     description=experience.description,
                                                     author_id=experience.author_id)
        return self._decode_db_experience(db_experience, is_mine=True)

    def attach_picture_to_experience(self, experience_id, picture):
        experience = ORMExperience.objects.get(id=experience_id)
        experience.picture = picture
        experience.save()
        return self._decode_db_experience(experience, is_mine=True)

    def update_experience(self, experience):
        orm_experience = ORMExperience.objects.get(id=experience.id)

        orm_experience.title = experience.title
        orm_experience.description = experience.description

        orm_experience.save()
        return self._decode_db_experience(orm_experience, is_mine=True)

    def save_experience(self, person_id, experience_id):
        if not ORMSave.objects.filter(person_id=person_id, experience_id=experience_id).exists():
            ORMSave.objects.create(person_id=person_id, experience_id=experience_id)
        return True

    def unsave_experience(self, person_id, experience_id):
        ORMSave.objects.filter(person_id=person_id, experience_id=experience_id).delete()
        return True
