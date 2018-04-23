from django.db.models import F

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
                          is_saved=is_saved,
                          saves_count=db_experience.saves_count)

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
            ORMExperience.objects.filter(id=experience_id).update(saves_count=F('saves_count') + 1)
        return True

    def unsave_experience(self, person_id, experience_id):
        deleted = ORMSave.objects.filter(person_id=person_id, experience_id=experience_id).delete()
        if deleted[0] == 1:
            ORMExperience.objects.filter(id=experience_id).update(saves_count=F('saves_count') - 1)

        return True


class ExperienceSearchRepo(object):

    EXPERIENCE_INDEX = 'experience_index'
    EXPERIENCE_DOC_TYPE = 'experience'

    def __init__(self, elastic_client):
        self.elastic_client = elastic_client

    def _create_experience_index(self):
        index = ExperienceSearchRepo.EXPERIENCE_INDEX
        body = {
            "settings": {
                "index": {
                    "number_of_shards": 3,
                    "number_of_replicas": 1
                }
            },
            "mappings": {
                ExperienceSearchRepo.EXPERIENCE_DOC_TYPE: {
                    "_source": {"enabled": False},
                    "properties": {
                        "title": {"type": "text"},
                        "description": {"type": "text"},
                        "scenes_titles": {"type": "text"},
                        "scenes_descriptions": {"type": "text"},
                        "author_id": {"type": "keyword"},
                        "saves_count": {"type": "integer"},
                        "center_location": {"type": "geo_point"}
                    }
                }
            }
        }
        self.elastic_client.indices.create(index=index, body=body)

    def _refresh_experience_index(self):
        self.elastic_client.indices.refresh(index=ExperienceSearchRepo.EXPERIENCE_INDEX)

    def _delete_experience_index(self):
        self.elastic_client.indices.delete(index=ExperienceSearchRepo.EXPERIENCE_INDEX)

    def index_experience_and_its_scenes(self, experience, scenes):
        scenes_titles = ' '.join([scene.title for scene in scenes])
        scenes_descriptions = ' '.join([scene.description for scene in scenes])
        doc = {
                'title': experience.title,
                'description': experience.description,
                'scenes_titles': scenes_titles,
                'scenes_descriptions': scenes_descriptions,
                'author_id': experience.author_id,
                'saves_count': experience.saves_count,
                'center_location': self._get_center_of_points([(scene.latitude, scene.longitude) for scene in scenes])
              }
        self.elastic_client.index(index=ExperienceSearchRepo.EXPERIENCE_INDEX,
                                  doc_type=ExperienceSearchRepo.EXPERIENCE_DOC_TYPE,
                                  body=doc, id=experience.id)

    def search_experiences(self, word, location=None, offset=0, limit=20):
        search_query = {
            'from': offset,
            'size': limit,
            'query': {
                'function_score': {
                    'query': {
                        'bool': {
                            'must': {
                                'bool': {
                                    'should': [
                                        {'match': {
                                            'title': {
                                                'query': word,
                                                'fuzziness': 'AUTO'
                                            }
                                        }},
                                        {'match': {
                                            'description': {
                                                'query': word,
                                                'fuzziness': 'AUTO'
                                            }
                                        }},
                                        {'match': {
                                            'scenes_titles': {
                                                'query': word,
                                                'fuzziness': 'AUTO'
                                            }
                                        }},
                                        {'match': {
                                            'scenes_descriptions': {
                                                'query': word,
                                                'fuzziness': 'AUTO'
                                            }
                                        }}
                                    ]
                                }
                            }
                        }
                    },
                    'functions': [
                        {'field_value_factor': {
                            'field': 'saves_count',
                            'modifier': 'log2p',
                            'factor': 0.1
                        }}
                    ]
                }
            }
        }

        if location is not None:
            location_decay = {'gauss': {
                'center_location': {
                    'origin': [location[0], location[1]],
                    'scale': '100km',
                    'offset': '0km',
                    'decay': 0.9
                }
            }}
            search_query['query']['function_score']['functions'].append(location_decay)

        res = self.elastic_client.search(index=ExperienceSearchRepo.EXPERIENCE_INDEX, body=search_query)
        return [x['_id'] for x in res['hits']['hits']]

    def _get_center_of_points(self, points):
        if len(points) == 0:
            return [0.0, 0.0]
        return [sum([p[0] for p in points]) / len(points),
                sum([p[1] for p in points]) / len(points)]
