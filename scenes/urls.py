from django.conf.urls import url

from pachatary.views import ViewWrapper
from .factories import create_scenes_view, create_scene_view, create_upload_scene_picture_view

urlpatterns = [
    url(r'^$',
        ViewWrapper.as_view(view_creator_func=create_scenes_view),
        name='scenes'),

    url(r'^(?P<scene_id>[0-9]+)$',
        ViewWrapper.as_view(view_creator_func=create_scene_view),
        name='scene'),

    url(r'^(?P<scene_id>[0-9]+)/picture$',
        ViewWrapper.as_view(view_creator_func=create_upload_scene_picture_view,
                            upload_picture_name='picture'),
        name='upload-scene-picture'),
]
