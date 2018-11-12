from django.conf.urls import url

from pachatary.views import ViewWrapper
from .factories import create_experiences_view, create_experience_view, \
        create_upload_experience_picture_view, create_save_experience_view, create_search_experiences_view, \
        create_experience_share_url_view, create_translate_experience_share_id_view, \
        create_flag_experience_view

urlpatterns = [
    url(r'^$',
        ViewWrapper.as_view(view_creator_func=create_experiences_view),
        name='experiences'),

    url(r'^search$',
        ViewWrapper.as_view(view_creator_func=create_search_experiences_view),
        name='search-experiences'),

    url(r'^(?P<experience_id>[0-9]+)$',
        ViewWrapper.as_view(view_creator_func=create_experience_view),
        name='experience'),

    url(r'^(?P<experience_id>[0-9]+)/share-url$',
        ViewWrapper.as_view(view_creator_func=create_experience_share_url_view),
        name='experience-share-url'),

    url(r'^(?P<experience_share_id>[a-zA-Z0-9]+)/id$',
        ViewWrapper.as_view(view_creator_func=create_translate_experience_share_id_view),
        name='translate-experience-share-id'),

    url(r'^(?P<experience_id>[0-9]+)/save$',
        ViewWrapper.as_view(view_creator_func=create_save_experience_view),
        name='experience-save'),

    url(r'^(?P<experience_id>[0-9]+)/flag$',
        ViewWrapper.as_view(view_creator_func=create_flag_experience_view),
        name='experience-flag'),

    url(r'^(?P<experience_id>[0-9]+)/picture$',
        ViewWrapper.as_view(view_creator_func=create_upload_experience_picture_view,
                            upload_picture_name='picture'),
        name='upload-experience-picture'),
]
