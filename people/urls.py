from django.conf.urls import url

from pachatary.views import ViewWrapper
from .factories import create_people_view, create_person_view, create_email_confirmation_view, \
        create_login_email_view, create_login_view, create_block_view

urlpatterns = [
    url(r'^$',
        ViewWrapper.as_view(view_creator_func=create_people_view),
        name='people'),

    url(r'^me$',
        ViewWrapper.as_view(view_creator_func=create_person_view),
        name='person'),

    url(r'^me/email-confirmation$',
        ViewWrapper.as_view(view_creator_func=create_email_confirmation_view),
        name='email-confirmation'),

    url(r'^me/login-email$',
        ViewWrapper.as_view(view_creator_func=create_login_email_view),
        name='login-email'),

    url(r'^me/login$',
        ViewWrapper.as_view(view_creator_func=create_login_view),
        name='login'),

    url(r'^(?P<username>[a-z0-9._]+)/block$',
        ViewWrapper.as_view(view_creator_func=create_block_view),
        name='person-block'),
]
