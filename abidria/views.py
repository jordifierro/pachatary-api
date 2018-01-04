import json
import urllib.parse

from django.http import HttpResponse
from django.views import View


class ViewWrapper(View):

    view_factory = None

    def get(self, request, *args, **kwargs):
        kwargs.update(request.GET.dict())
        body, status = self.view_factory.create().get(**kwargs)
        return HttpResponse(json.dumps(body), status=status, content_type='application/json')

    def post(self, request, *args, **kwargs):
        kwargs.update(request.POST.dict())
        body, status = self.view_factory.create().post(**kwargs)
        return HttpResponse(json.dumps(body), status=status, content_type='application/json')

    def patch(self, request, *args, **kwargs):
        data = dict(urllib.parse.parse_qsl(request.body.decode("utf-8"), keep_blank_values=True))
        kwargs.update(data)
        body, status = self.view_factory.create().patch(**kwargs)
        return HttpResponse(json.dumps(body), status=status, content_type='application/json')
