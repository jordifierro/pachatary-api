from django.http import HttpResponse
from django.conf import settings

ANDROID_EMAIL_CONFIRMATION_PATH = '/people/me/email-confirmation'
ANDROID_LOGIN_PATH = '/people/me/login'


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
