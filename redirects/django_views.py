from django.http import HttpResponse
from django.conf import settings

EMAIL_CONFIRMATION_PATH = '/people/me/email-confirmation'
LOGIN_PATH = '/people/me/login'
EXPERIENCE_PATH = '/e'
PROFILE_PATH = '/p'
EXPERIENCE_DEEPLINK_PATH = '/experiences'
PROFILE_DEEPLINK_PATH = '/profiles'


def email_confirmation_redirect(request):
    response = HttpResponse('', status=302)
    response['Location'] = '{}{}?{}'.format(settings.APP_DEEPLINK_DOMAIN,
                                            EMAIL_CONFIRMATION_PATH, request.GET.urlencode())
    return response


def login_redirect(request):
    response = HttpResponse('', status=302)
    response['Location'] = '{}{}?{}'.format(settings.APP_DEEPLINK_DOMAIN,
                                            LOGIN_PATH, request.GET.urlencode())
    return response


def experience_redirect(request, experience_share_id):
    dynamic_link = settings.DYNAMIC_LINK
    if len(dynamic_link) > 0:
        real_link = '{}{}/{}'.format(settings.PUBLIC_DOMAIN, EXPERIENCE_PATH, experience_share_id)
        link = dynamic_link.format(real_link)
    else:
        link = '{}{}/{}'.format(settings.APP_DEEPLINK_DOMAIN, EXPERIENCE_DEEPLINK_PATH, experience_share_id)

    response = HttpResponse('', status=302)
    response['Location'] = link
    return response


def profile_redirect(request, username):
    dynamic_link = settings.DYNAMIC_LINK
    if len(dynamic_link) > 0:
        real_link = '{}{}/{}'.format(settings.PUBLIC_DOMAIN, PROFILE_PATH, username)
        link = dynamic_link.format(real_link)
    else:
        link = '{}{}/{}'.format(settings.APP_DEEPLINK_DOMAIN, PROFILE_DEEPLINK_PATH, username)

    response = HttpResponse('', status=302)
    response['Location'] = link
    return response


def root_redirect(request):
    dynamic_link = settings.DYNAMIC_LINK
    if len(dynamic_link) > 0:
        link = dynamic_link.format(settings.PUBLIC_DOMAIN)
    else:
        link = '{}/'.format(settings.APP_DEEPLINK_DOMAIN)

    response = HttpResponse('', status=302)
    response['Location'] = link
    return response
