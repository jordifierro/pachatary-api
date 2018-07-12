from pachatary.serializers import serialize_picture


def serialize_profile(profile):
    return {
               'person_id': str(profile.person_id),
               'username': profile.username,
               'bio': profile.bio,
               'picture': serialize_picture(profile.picture),
           }
