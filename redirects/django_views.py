from django.http import HttpResponse
from django.conf import settings

ANDROID_EMAIL_CONFIRMATION_PATH = '/people/me/email-confirmation'
ANDROID_LOGIN_PATH = '/people/me/login'
ANDROID_EXPERIENCE_PATH = '/e'
ANDROID_PROFILE_PATH = '/p'


def email_confirmation_redirect(request):
    response = HttpResponse('', status=302)
    response['Location'] = '{}{}?{}'.format(settings.ANDROID_DEEPLINK_DOMAIN,
                                            ANDROID_EMAIL_CONFIRMATION_PATH, request.GET.urlencode())
    return response


def login_redirect(request):
    response = HttpResponse('', status=302)
    response['Location'] = '{}{}?{}'.format(settings.ANDROID_DEEPLINK_DOMAIN,
                                            ANDROID_LOGIN_PATH, request.GET.urlencode())
    return response


def experience_redirect(request, experience_share_id):
    dynamic_link = settings.DYNAMIC_LINK
    if len(dynamic_link) > 0:
        real_link = '{}{}/{}'.format(settings.PUBLIC_DOMAIN, ANDROID_EXPERIENCE_PATH, experience_share_id)
        link = dynamic_link.format(real_link)
    else:
        link = '{}{}/{}'.format(settings.ANDROID_DEEPLINK_DOMAIN, ANDROID_EXPERIENCE_PATH, experience_share_id)

    response = HttpResponse('', status=302)
    response['Location'] = link
    return response


def profile_redirect(request, username):
    dynamic_link = settings.DYNAMIC_LINK
    if len(dynamic_link) > 0:
        real_link = '{}{}/{}'.format(settings.PUBLIC_DOMAIN, ANDROID_PROFILE_PATH, username)
        link = dynamic_link.format(real_link)
    else:
        link = '{}{}/{}'.format(settings.ANDROID_DEEPLINK_DOMAIN, ANDROID_PROFILE_PATH, username)

    response = HttpResponse('', status=302)
    response['Location'] = link
    return response


def root_redirect(request):
    dynamic_link = settings.DYNAMIC_LINK
    if len(dynamic_link) > 0:
        link = dynamic_link.format(settings.PUBLIC_DOMAIN)
    else:
        link = '{}/'.format(settings.ANDROID_DEEPLINK_DOMAIN)

    response = HttpResponse('', status=302)
    response['Location'] = link
    return response
