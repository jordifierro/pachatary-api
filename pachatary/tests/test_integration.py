import json

from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings


class ClientVersionsTestCase(TestCase):

    def test_client_version_returns_settings_android_min_version(self):
        ClientVersionsTestCase.ScenarioMaker() \
                .given_an_android_min_version_on_settings() \
                .when_call_client_version() \
                .then_response_should_be_android_min_version()

    class ScenarioMaker:

        def given_an_android_min_version_on_settings(self):
            self.android_min_version = 4
            settings.ANDROID_MIN_VERSION = self.android_min_version
            return self

        def when_call_client_version(self):
            self.response = Client().get(reverse('client-versions'))
            return self

        def then_response_should_be_android_min_version(self):
            assert json.loads(self.response.content) == {'android': {'min_version': self.android_min_version}}
            assert self.response.status_code == 200
