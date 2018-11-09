import json

from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings


class ClientVersionsTestCase(TestCase):

    def test_client_version_returns_settings_android_min_version(self):
        ClientVersionsTestCase.ScenarioMaker() \
                .given_an_android_min_version_on_settings(4) \
                .given_an_ios_min_version_on_settings(3) \
                .when_call_client_version() \
                .then_response_should_be(android_min_version=4, ios_min_version=3)

    class ScenarioMaker:

        def given_an_android_min_version_on_settings(self, version):
            settings.ANDROID_MIN_VERSION = version
            return self

        def given_an_ios_min_version_on_settings(self, version):
            settings.IOS_MIN_VERSION = version
            return self

        def when_call_client_version(self):
            self.response = Client().get(reverse('client-versions'))
            return self

        def then_response_should_be(self, android_min_version, ios_min_version):
            assert json.loads(self.response.content) == {
                    'android': {'min_version': android_min_version},
                    'ios': {'min_version': ios_min_version},
                }
            assert self.response.status_code == 200
