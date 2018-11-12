from elasticsearch import NotFoundError as ElasticSearchNotFoundError

from django.db.models import F, Case, When
from django.db import IntegrityError

from pachatary.entities import Picture
from pachatary.exceptions import EntityDoesNotExistException, ConflictException
from profiles.entities import Profile
from .models import ORMExperience, ORMSave, ORMFlag
from .entities import Experience


class ExperienceRepo:

    def __init__(self, search_repo=None):
        self.search_repo = search_repo

    def _decode_db_experience(self, db_experience, logged_person_id, is_saved=False):
        if not db_experience.picture:
            picture = None
        else:
            picture = Picture(small_url=db_experience.picture.small.url,
                              medium_url=db_experience.picture.medium.url,
                              large_url=db_experience.picture.large.url)

        author_profile = self._decode_db_profile(db_experience.author.profile, logged_person_id)
        return Experience(id=str(db_experience.id),
                          title=db_experience.title,
                          description=db_experience.description,
                          picture=picture,
                          author_id=str(db_experience.author_id),
                          author_profile=author_profile,
                          is_mine=(logged_person_id == author_profile.person_id),
                          is_saved=is_saved,
                          saves_count=db_experience.saves_count,
                          share_id=db_experience.share_id)

    def _decode_db_profile(self, db_profile, logged_person_id):
        if not db_profile.picture:
            picture = None
        else:
            picture = Picture(tiny_url=db_profile.picture.tiny.url,
                              small_url=db_profile.picture.small.url,
                              medium_url=db_profile.picture.medium.url)
        return Profile(person_id=str(db_profile.person_id),
                       username=db_profile.username,
                       bio=db_profile.bio,
                       picture=picture,
                       is_me=(str(db_profile.person_id) == logged_person_id))

    def get_saved_experiences(self, logged_person_id, offset=0, limit=100):
        db_saves_and_experiences = ORMSave.objects \
                                          .order_by('-id') \
                                          .select_related('experience', 'experience__author__profile') \
                                          .exclude(experience__is_deleted=True) \
                                          .filter(person_id=logged_person_id)

        paginated_db_saves = db_saves_and_experiences[offset:offset+limit+1]
        next_offset = None
        if len(paginated_db_saves) == limit+1:
            next_offset = offset + limit

        experiences = []
        for db_save in paginated_db_saves[0:limit]:
            experiences.append(self._decode_db_experience(db_save.experience, logged_person_id, is_saved=True))
        return {'results': experiences, 'next_offset': next_offset}

    def get_person_experiences(self, logged_person_id, target_person_id, offset=0, limit=100, mine=False, saved=False):
        person_db_experiences = ORMExperience.objects \
                                                .exclude(is_deleted=True) \
                                                .order_by('-id') \
                                                .select_related('author__profile') \
                                                .filter(author_id=target_person_id)

        paginated_db_experiences = person_db_experiences[offset:offset+limit+1]
        next_offset = None
        if len(paginated_db_experiences) == limit+1:
            next_offset = offset + limit

        are_my_experiences = (logged_person_id == target_person_id)
        if not are_my_experiences:
            orm_my_saves = list(ORMSave.objects.filter(person_id=logged_person_id))

        experiences = []
        for db_experience in paginated_db_experiences[0:limit]:
            is_saved = False
            if not are_my_experiences and len([x for x in orm_my_saves if x.experience_id == db_experience.id]) > 0:
                is_saved = True
            experiences.append(self._decode_db_experience(db_experience, logged_person_id, is_saved=is_saved))
        return {"results": experiences, "next_offset": next_offset}

    def get_experience(self, id=None, share_id=None, logged_person_id=None):
        try:
            if id is not None:
                db_experience = ORMExperience.objects \
                                                .exclude(is_deleted=True) \
                                                .select_related('author__profile').get(id=id)
            else:
                db_experience = ORMExperience.objects \
                                                .exclude(is_deleted=True) \
                                                .select_related('author__profile').get(share_id=share_id)
            is_mine = (logged_person_id == db_experience.author_id)
            is_saved = False
            if logged_person_id is not None and not is_mine:
                is_saved = ORMSave.objects.filter(experience_id=id, person_id=logged_person_id).exists()
            return self._decode_db_experience(db_experience, logged_person_id, is_saved=is_saved)
        except ORMExperience.DoesNotExist:
            raise EntityDoesNotExistException()

    def create_experience(self, experience):
        db_experience = ORMExperience.objects.create(title=experience.title,
                                                     description=experience.description,
                                                     author_id=experience.author_id)
        return self._decode_db_experience(db_experience, str(db_experience.author_id))

    def attach_picture_to_experience(self, experience_id, picture):
        experience = ORMExperience.objects.get(id=experience_id)
        experience.picture = picture
        experience.save()
        return self._decode_db_experience(experience, str(experience.author_id))

    def update_experience(self, experience, logged_person_id=None):
        orm_experience = ORMExperience.objects.get(id=experience.id)

        orm_experience.title = experience.title
        orm_experience.description = experience.description
        orm_experience.share_id = experience.share_id

        try:
            orm_experience.save()
        except IntegrityError:
            raise ConflictException(source='share_id', code='duplicate', message='Duplicate share_id')
        return self._decode_db_experience(orm_experience, logged_person_id)

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

    def flag_experience(self, person_id, experience_id, reason):
        ORMFlag.objects.create(person_id=person_id, experience_id=experience_id, reason=reason)
        return True

    def search_experiences(self, logged_person_id, word, location=None, offset=0, limit=20):
        result = self.search_repo.search_experiences(word, location, offset, limit)
        experiences = self._populate(logged_person_id, result['results'])
        return {'results': experiences, 'next_offset': result['next_offset']}

    def _populate(self, logged_person_id, experiences_ids):
        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(experiences_ids)])
        orm_experiences = ORMExperience.objects.select_related('author__profile') \
                                               .filter(id__in=experiences_ids) \
                                               .order_by(preserved)
        orm_saves = list(ORMSave.objects.filter(experience_id__in=experiences_ids, person_id=logged_person_id))
        return [self._decode_db_experience(experience, logged_person_id,
                                           len([x for x in orm_saves if x.experience_id == experience.id]) > 0)
                for experience in orm_experiences]


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

    def delete_experience(self, experience_id):
        try:
            self.elastic_client.delete(index=ExperienceSearchRepo.EXPERIENCE_INDEX,
                                       doc_type=ExperienceSearchRepo.EXPERIENCE_DOC_TYPE,
                                       id=experience_id)
        except ElasticSearchNotFoundError:
            pass

    def search_experiences(self, word=None, location=None, offset=0, limit=20):
        search_query = {
            'from': offset,
            'size': limit + 1,
            'query': {
                'function_score': {
                    'query': {},
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

        if word is not None:
            search_by_word = {
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
            }
            search_query['query']['function_score']['query'].update(search_by_word)
        else:
            search_query['query']['function_score']['query'].update({'match_all': {}})

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

        next_offset = None
        if len(res['hits']['hits']) == limit + 1:
            next_offset = offset + limit

        return {'results': [x['_id'] for x in res['hits']['hits'][0:limit]],
                'next_offset': next_offset}

    def _get_center_of_points(self, points):
        if len(points) == 0:
            return [0.0, 0.0]
        return [sum([p[0] for p in points]) / len(points),
                sum([p[1] for p in points]) / len(points)]
