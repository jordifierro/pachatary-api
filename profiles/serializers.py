from pachatary.serializers import serialize_picture


def serialize_profile(profile):
    return {
               'username': profile.username,
               'bio': profile.bio,
               'picture': serialize_picture(profile.picture),
               'is_me': profile.is_me
           }
