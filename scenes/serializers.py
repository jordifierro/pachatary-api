from pachatary.serializers import serialize_picture


def serialize_multiple_scenes(scenes):
    return [serialize_scene(scene) for scene in scenes]


def serialize_scene(scene):
    return {
               'id': str(scene.id),
               'title': scene.title,
               'description': scene.description,
               'picture': serialize_picture(scene.picture),
               'latitude': float(scene.latitude),
               'longitude': float(scene.longitude),
               'experience_id': str(scene.experience_id),
           }
