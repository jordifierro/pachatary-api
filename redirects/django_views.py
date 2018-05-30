from django.http import HttpResponse
from django.conf import settings

ANDROID_EMAIL_CONFIRMATION_PATH = '/people/me/email-confirmation'
ANDROID_LOGIN_PATH = '/people/me/login'
ANDROID_EXPERIENCE_PATH = '/experiences'


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
    response = HttpResponse('', status=302)
    response['Location'] = '{}{}/{}'.format(settings.ANDROID_DEEPLINK_DOMAIN,
                                            ANDROID_EXPERIENCE_PATH, experience_share_id)
    return response
