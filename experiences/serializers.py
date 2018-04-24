from pachatary.serializers import PictureSerializer


class ExperiencesResponseSerializer:

    @staticmethod
    def serialize(experiences, base_url, mine, saved, next_limit, next_offset):
        if next_offset is not None:
            next_url = '{}?mine={}&saved={}&limit={}&offset={}'.format(base_url, mine, saved, next_limit, next_offset)
        else:
            next_url = None

        return {'results': MultipleExperiencesSerializer.serialize(experiences), 'next_url': next_url}


class ExperiencesSearchResponseSerializer:

    @staticmethod
    def serialize(experiences, base_url, query, latitude, longitude, next_limit, next_offset):
        if next_offset is not None:
            next_url = '{}?query={}&limit={}&offset={}'.format(base_url, query, next_limit, next_offset)
            if latitude is not None:
                next_url = "{}&latitude={}".format(next_url, latitude)
            if longitude is not None:
                next_url = "{}&longitude={}".format(next_url, longitude)
        else:
            next_url = None

        return {'results': experiences, 'next_url': next_url}


class MultipleExperiencesSerializer:

    @staticmethod
    def serialize(experiences):
        return [ExperienceSerializer.serialize(experience) for experience in experiences]


class ExperienceSerializer:

    @staticmethod
    def serialize(experience):
        return {
                   'id': str(experience.id),
                   'title': experience.title,
                   'description': experience.description,
                   'picture': PictureSerializer.serialize(experience.picture),
                   'author_id': experience.author_id,
                   'author_username': experience.author_username,
                   'is_mine': experience.is_mine,
                   'is_saved': experience.is_saved,
                   'saves_count': experience.saves_count
               }
