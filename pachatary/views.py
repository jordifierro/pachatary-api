import json
import urllib.parse

from django.template.loader import get_template
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.conf import settings

from people.factories import create_authenticate_interactor


class ViewWrapper(View):

    view_creator_func = None
    upload_picture_name = None

    def get(self, request, *args, **kwargs):
        kwargs.update(request.GET.dict())

        logged_person_id = self.authenticate(request, **kwargs)
        request.logged_person_id = logged_person_id
        kwargs.update({'logged_person_id': logged_person_id})

        body, status = self.view_creator_func(request, **kwargs).get(**kwargs)
        return HttpResponse(json.dumps(body), status=status, content_type='application/json')

    def post(self, request, *args, **kwargs):
        kwargs.update(request.POST.dict())

        logged_person_id = self.authenticate(request, **kwargs)
        request.logged_person_id = logged_person_id
        kwargs.update({'logged_person_id': logged_person_id})

        if self.upload_picture_name is not None:
            picture = request.FILES[self.upload_picture_name]
            body, status = self.view_creator_func(request, **kwargs).post(picture, **kwargs)
        else:
            body, status = self.view_creator_func(request, **kwargs).post(**kwargs)
        content = json.dumps(body) if body is not None else ''
        return HttpResponse(content, status=status, content_type='application/json')

    def patch(self, request, *args, **kwargs):
        data = dict(urllib.parse.parse_qsl(request.body.decode("utf-8"), keep_blank_values=True))
        kwargs.update(data)

        logged_person_id = self.authenticate(request, **kwargs)
        request.logged_person_id = logged_person_id
        kwargs.update({'logged_person_id': logged_person_id})

        if self.upload_picture_name is not None:
            picture = request.FILES[self.upload_picture_name]
            body, status = self.view_creator_func(request, **kwargs).patch(picture, **kwargs)
        else:
            body, status = self.view_creator_func(request, **kwargs).patch(**kwargs)
        content = json.dumps(body) if body is not None else ''
        return HttpResponse(content, status=status, content_type='application/json')

    def delete(self, request, *args, **kwargs):
        data = dict(urllib.parse.parse_qsl(request.body.decode("utf-8"), keep_blank_values=True))
        kwargs.update(data)

        logged_person_id = self.authenticate(request, **kwargs)
        request.logged_person_id = logged_person_id
        kwargs.update({'logged_person_id': logged_person_id})

        body, status = self.view_creator_func(request, **kwargs).delete(**kwargs)
        content = json.dumps(body) if body is not None else ''
        return HttpResponse(content, status=status, content_type='application/json')

    def authenticate(self, request, **kwargs):
        authentication_header = request.META.get('HTTP_AUTHORIZATION')
        if authentication_header is None:
            return None

        access_token = authentication_header.replace('Token ', '')
        return create_authenticate_interactor().set_params(access_token=access_token).execute()


def client_versions(request):
    response = {
        'android': {
            'min_version': int(settings.ANDROID_MIN_VERSION)
        },
        'ios': {
            'min_version': int(settings.IOS_MIN_VERSION)
        }
    }

    return HttpResponse(json.dumps(response), status=200)


def privacy_policy(request):
    return HttpResponse(get_template('privacy_policy.html').render())


def terms_and_conditions(request):
    return HttpResponse(get_template('terms_and_conditions.html').render())


def aasa_redirect(request):
    return JsonResponse({"applinks": {"apps": [], "details": [{"appID": settings.APPLE_APPID, "paths": ["*"]}]}})
