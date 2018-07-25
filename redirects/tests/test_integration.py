from django.conf import settings
from django.test import TestCase, Client
from django.urls import reverse


class RedirectConfirmEmailTestCase(TestCase):

    def test_when_called_redirect_view_redirects_to_apps_url(self):
        RedirectConfirmEmailTestCase.ScenarioMaker() \
                .when_call_get_email_confirmation() \
                .then_response_should_be_a_redirect_to_app_deeplink_with_params()

    class ScenarioMaker:

        def when_call_get_email_confirmation(self):
            client = Client()
            self.response = client.get('{}?{}'.format(reverse('email-confirmation-redirect'), 'token=ABXZ'))
            return self

        def then_response_should_be_a_redirect_to_app_deeplink_with_params(self):
            assert self.response.status_code == 302
            assert self.response['Location'] == '{}{}?token=ABXZ'.format(settings.ANDROID_DEEPLINK_DOMAIN,
                                                                         '/people/me/email-confirmation')
            return self


class RedirectLoginEmailTestCase(TestCase):

    def test_when_called_redirect_view_redirects_to_apps_url(self):
        RedirectLoginEmailTestCase.ScenarioMaker() \
                .when_call_login_email_redirect() \
                .then_response_should_be_a_redirect_to_app_deeplink_with_params()

    class ScenarioMaker:

        def when_call_login_email_redirect(self):
            client = Client()
            self.response = client.get('{}?{}'.format(reverse('login-redirect'), 'token=ABXZ'))
            return self

        def then_response_should_be_a_redirect_to_app_deeplink_with_params(self):
            assert self.response.status_code == 302
            assert self.response['Location'] == '{}{}?token=ABXZ'.format(settings.ANDROID_DEEPLINK_DOMAIN,
                                                                         '/people/me/login')
            return self


class RedirectExperienceTestCase(TestCase):

    def test_when_called_redirect_view_redirects_to_experience_url(self):
        RedirectExperienceTestCase.ScenarioMaker() \
                .when_call_experience_redirect() \
                .then_response_should_be_a_redirect_to_app_deeplink_with_params()

    class ScenarioMaker:

        def when_call_experience_redirect(self):
            client = Client()
            self.response = client.get(reverse('experience-redirect', args=['AsdE43E4']))
            return self

        def then_response_should_be_a_redirect_to_app_deeplink_with_params(self):
            assert self.response.status_code == 302
            assert self.response['Location'] == '{}/experiences/AsdE43E4'.format(settings.ANDROID_DEEPLINK_DOMAIN)
            return self


class RedirectProfileTestCase(TestCase):

    def test_when_called_redirect_view_redirects_to_profile_url(self):
        RedirectProfileTestCase.ScenarioMaker() \
                .when_call_profile_redirect() \
                .then_response_should_be_a_redirect_to_app_deeplink_with_params()

    class ScenarioMaker:

        def when_call_profile_redirect(self):
            client = Client()
            self.response = client.get(reverse('profile-redirect', args=['a_b.c']))
            return self

        def then_response_should_be_a_redirect_to_app_deeplink_with_params(self):
            assert self.response.status_code == 302
            assert self.response['Location'] == '{}/profiles/a_b.c'.format(settings.ANDROID_DEEPLINK_DOMAIN)
            return self
