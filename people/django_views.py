from django.http import HttpResponse
from django.conf import settings

ANDROID_DEEPLINK_PATH = '/people/me/email-confirmation'


def email_confirmation_redirect(request):
    response = HttpResponse('', status=302)
    response['Location'] = '{}{}?{}'.format(settings.ANDROID_DEEPLINK_DOMAIN,
                                            ANDROID_DEEPLINK_PATH, request.GET.urlencode())
    return response
