from urllib.parse import urlencode, quote_plus

from django.http import HttpResponse, JsonResponse
from django.conf import settings

from experiences.factories import create_get_experience_interactor
from profiles.factories import create_get_profile_interactor

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

        get_experience_interactor = create_get_experience_interactor()
        experience = get_experience_interactor.set_params(experience_share_id=experience_share_id,
                                                          logged_person_id='-1') \
                                              .execute()
        desc = (experience.description[:77] + '...') if len(experience.description) > 77 else experience.description
        preview_content = {'st': experience.title, 'sd': desc, 'si': experience.picture.small_url}
        preview_encoded = urlencode(preview_content, quote_via=quote_plus)
        link = '{}&{}'.format(link, preview_encoded)
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

        get_profile_interactor = create_get_profile_interactor()
        profile = get_profile_interactor.set_params(username=username, logged_person_id='-1').execute()
        preview_content = {'st': '@{}'.format(profile.username), 'sd': profile.bio, 'si': profile.picture.small_url}
        preview_encoded = urlencode(preview_content, quote_via=quote_plus)
        link = '{}&{}'.format(link, preview_encoded)
    else:
        link = '{}{}/{}'.format(settings.APP_DEEPLINK_DOMAIN, PROFILE_DEEPLINK_PATH, username)

    response = HttpResponse('', status=302)
    response['Location'] = link
    return response


def root_redirect(request):
    dynamic_link = settings.DYNAMIC_LINK
    if len(dynamic_link) > 0:
        link = dynamic_link.format('{}/'.format(settings.PUBLIC_DOMAIN))
    else:
        link = '{}/'.format(settings.APP_DEEPLINK_DOMAIN)

    response = HttpResponse('', status=302)
    response['Location'] = link
    return response


def aasa_redirect(request):
    return JsonResponse({"applinks": {"apps": [], "details": [{"appID": settings.APPLE_APPID, "paths": ["*"]}]}})
