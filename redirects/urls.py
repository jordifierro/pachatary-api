from django.conf.urls import url

from .django_views import email_confirmation_redirect, login_redirect, experience_redirect, profile_redirect, \
        root_redirect, aasa_redirect

urlpatterns = [
    url(r'^people/me/email-confirmation$',
        email_confirmation_redirect,
        name='email-confirmation-redirect'),

    url(r'^people/me/login$',
        login_redirect,
        name='login-redirect'),

    url(r'^e/(?P<experience_share_id>[a-zA-Z0-9]+)$',
        experience_redirect,
        name='experience-redirect'),

    url(r'^p/(?P<username>[a-zA-Z0-9._]+)$',
        profile_redirect,
        name='profile-redirect'),

    url(r'^apple-app-site-association$',
        aasa_redirect,
        name='aasa'),

    url(r'^$',
        root_redirect,
        name='root-redirect'),
]
