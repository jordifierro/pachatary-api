from pachatary.serializers import serialize_picture
from profiles.serializers import serialize_profile


def serialize_experiences_response(experiences, base_url, username, saved, next_limit, next_offset):
    if next_offset is not None:
        if saved:
            next_url = '{}?saved=true&limit={}&offset={}'.format(base_url, next_limit, next_offset)
        else:
            next_url = '{}?username={}&limit={}&offset={}'.format(base_url, username, next_limit, next_offset)

    else:
        next_url = None

    return {'results': serialize_multiple_experiences(experiences), 'next_url': next_url}


def serialize_experiences_search_response(experiences, base_url, word, latitude, longitude, next_limit, next_offset):
    if next_offset is not None:
        next_url = '{}?offset={}&limit={}'.format(base_url, next_offset, next_limit)
        if word is not None:
            next_url = "{}&word={}".format(next_url, word)
        if latitude is not None:
            next_url = "{}&latitude={}".format(next_url, latitude)
        if longitude is not None:
            next_url = "{}&longitude={}".format(next_url, longitude)
    else:
        next_url = None

    return {'results': serialize_multiple_experiences(experiences), 'next_url': next_url}


def serialize_multiple_experiences(experiences):
    return [serialize_experience(experience) for experience in experiences]


def serialize_experience(experience):
    return {
               'id': str(experience.id),
               'title': experience.title,
               'description': experience.description,
               'picture': serialize_picture(experience.picture),
               'author_profile': serialize_profile(experience.author_profile),
               'is_mine': experience.is_mine,
               'is_saved': experience.is_saved,
               'saves_count': experience.saves_count
           }
