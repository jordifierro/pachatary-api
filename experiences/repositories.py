from abidria.entities import Picture
from abidria.exceptions import EntityDoesNotExistException
from .models import ORMExperience
from .entities import Experience


class ExperienceRepo(object):

    def _decode_db_experience(self, db_experience):
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
                          author_username=db_experience.author.username)

    def get_all_experiences(self, logged_person_id, mine):
        all_db_experiences = ORMExperience.objects.select_related('author').all()
        if mine:
            db_experiences = all_db_experiences.filter(author_id=logged_person_id)
        else:
            db_experiences = all_db_experiences.exclude(author_id=logged_person_id)

        experiences = []
        for db_experience in db_experiences:
            experiences.append(self._decode_db_experience(db_experience))
        return experiences

    def get_experience(self, id):
        try:
            db_experience = ORMExperience.objects.select_related('author').get(id=id)
            return self._decode_db_experience(db_experience)
        except ORMExperience.DoesNotExist:
            raise EntityDoesNotExistException()

    def create_experience(self, experience):
        db_experience = ORMExperience.objects.create(title=experience.title,
                                                     description=experience.description,
                                                     author_id=experience.author_id)
        return self._decode_db_experience(db_experience)

    def attach_picture_to_experience(self, experience_id, picture):
        experience = ORMExperience.objects.get(id=experience_id)
        experience.picture = picture
        experience.save()
        return self._decode_db_experience(experience)

    def update_experience(self, experience):
        orm_experience = ORMExperience.objects.get(id=experience.id)

        orm_experience.title = experience.title
        orm_experience.description = experience.description

        orm_experience.save()
        return self._decode_db_experience(orm_experience)
