from django.conf.urls import url
from django.urls import include, path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from experiences.factories import create_experiences_view, create_experience_view, \
        create_upload_experience_picture_view, create_save_experience_view, create_search_experiences_view, \
        create_experience_share_url_view, create_translate_experience_share_id_view
from scenes.factories import create_scenes_view, create_scene_view, create_upload_scene_picture_view
from people.factories import create_people_view, create_person_view, create_email_confirmation_view, \
        create_login_email_view, create_login_view
from profiles.factories import create_profile_view, create_upload_profile_picture_view
from redirects.django_views import email_confirmation_redirect, login_redirect, experience_redirect, profile_redirect

from .views import ViewWrapper, client_versions, privacy_policy, terms_and_conditions

app_name = 'pachatary'
urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^experiences/$',
        ViewWrapper.as_view(view_creator_func=create_experiences_view),
        name='experiences'),

    url(r'^experiences/search$',
        ViewWrapper.as_view(view_creator_func=create_search_experiences_view),
        name='search-experiences'),

    url(r'^experiences/(?P<experience_id>[0-9]+)$',
        ViewWrapper.as_view(view_creator_func=create_experience_view),
        name='experience'),

    url(r'^experiences/(?P<experience_id>[0-9]+)/share-url$',
        ViewWrapper.as_view(view_creator_func=create_experience_share_url_view),
        name='experience-share-url'),

    url(r'^experiences/(?P<experience_share_id>[a-zA-Z0-9]+)/id$',
        ViewWrapper.as_view(view_creator_func=create_translate_experience_share_id_view),
        name='translate-experience-share-id'),

    url(r'experiences/(?P<experience_id>[0-9]+)/save$',
        ViewWrapper.as_view(view_creator_func=create_save_experience_view),
        name='experience-save'),

    url(r'experiences/(?P<experience_id>[0-9]+)/picture$',
        ViewWrapper.as_view(view_creator_func=create_upload_experience_picture_view,
                            upload_picture_name='picture'),
        name='upload-experience-picture'),

    url(r'^scenes/$',
        ViewWrapper.as_view(view_creator_func=create_scenes_view),
        name='scenes'),

    url(r'^scenes/(?P<scene_id>[0-9]+)$',
        ViewWrapper.as_view(view_creator_func=create_scene_view),
        name='scene'),

    url(r'scenes/(?P<scene_id>[0-9]+)/picture$',
        ViewWrapper.as_view(view_creator_func=create_upload_scene_picture_view,
                            upload_picture_name='picture'),
        name='upload-scene-picture'),

    url(r'^people/$',
        ViewWrapper.as_view(view_creator_func=create_people_view),
        name='people'),

    url(r'^people/me$',
        ViewWrapper.as_view(view_creator_func=create_person_view),
        name='person'),

    url(r'^people/me/email-confirmation$',
        ViewWrapper.as_view(view_creator_func=create_email_confirmation_view),
        name='email-confirmation'),

    url(r'^people/me/login-email$',
        ViewWrapper.as_view(view_creator_func=create_login_email_view),
        name='login-email'),

    url(r'^people/me/login$',
        ViewWrapper.as_view(view_creator_func=create_login_view),
        name='login'),

    url(r'^client-versions$',
        client_versions,
        name='client-versions'),

    url(r'^privacy-policy$',
        privacy_policy,
        name='privacy-policy'),

    url(r'^terms-and-conditions$',
        terms_and_conditions,
        name='terms-and-conditions'),

    url(r'^redirects/people/me/email-confirmation$',
        email_confirmation_redirect,
        name='email-confirmation-redirect'),

    url(r'^redirects/people/me/login$',
        login_redirect,
        name='login-redirect'),

    url(r'^redirects/e/(?P<experience_share_id>[a-zA-Z0-9]+)$',
        experience_redirect,
        name='experience-redirect'),

    url(r'^profiles/(?P<username>[a-z0-9._]+)$',
        ViewWrapper.as_view(view_creator_func=create_profile_view),
        name='profile'),

    url(r'profiles/me/picture$',
        ViewWrapper.as_view(view_creator_func=create_upload_profile_picture_view,
                            upload_picture_name='picture'),
        name='upload-profile-picture'),

    url(r'^redirects/p/(?P<username>[a-zA-Z0-9._]+)$',
        profile_redirect,
        name='profile-redirect'),
]

if settings.LOCAL_DEPLOY:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [path('django-rq/', include('django_rq.urls'))]
