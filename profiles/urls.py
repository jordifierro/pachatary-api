from django.conf.urls import url

from pachatary.views import ViewWrapper
from .factories import create_profile_view, create_upload_profile_picture_view

urlpatterns = [
    url(r'^(?P<username>[a-z0-9._]+)$',
        ViewWrapper.as_view(view_creator_func=create_profile_view),
        name='profile'),

    url(r'^me/picture$',
        ViewWrapper.as_view(view_creator_func=create_upload_profile_picture_view,
                            upload_picture_name='picture'),
        name='upload-profile-picture'),
]
