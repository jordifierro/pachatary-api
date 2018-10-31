import json

from django.conf import settings
from django.test import TestCase, Client
from django.urls import reverse

from experiences.models import ORMExperience
from people.models import ORMPerson
from profiles.models import ORMProfile


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
            assert self.response['Location'] == '{}{}?token=ABXZ'.format(settings.APP_DEEPLINK_DOMAIN,
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
            assert self.response['Location'] == '{}{}?token=ABXZ'.format(settings.APP_DEEPLINK_DOMAIN,
                                                                         '/people/me/login')
            return self


class RedirectExperienceTestCase(TestCase):

    def test_when_there_is_a_dynamic_link_wraps_public_domain_url(self):
        RedirectExperienceTestCase.ScenarioMaker() \
                .given_an_experience_on_db(title='a', description='d', share_id='AsdE43E4', pic='url') \
                .given_a_public_domain('http://pachatary.com') \
                .given_a_dynamic_link('http://dynamic.link/link={}&other=param') \
                .when_call_experience_redirect('AsdE43E4') \
                .then_response_should_be_a_redirect_to(
                    'http://dynamic.link/link=http://pachatary.com/e/AsdE43E4&other=param'
                    '&st=a&sd=d&si=%2Fmedia%2Furl.small')

    def test_when_there_is_no_dynamic_link_returns_deep_link(self):
        RedirectExperienceTestCase.ScenarioMaker() \
                .given_a_deep_link_domain('pachatary://app') \
                .given_a_dynamic_link('') \
                .when_call_experience_redirect('AsdE43E4') \
                .then_response_should_be_a_redirect_to('pachatary://app/experiences/AsdE43E4')

    class ScenarioMaker:

        def given_an_experience_on_db(self, title, description, share_id, pic):
            orm_person = ORMPerson.objects.create()
            ORMProfile.objects.create(person=orm_person, username='u')
            experience = ORMExperience.objects.create(title=title, description=description,
                                                      share_id=share_id, author=orm_person)
            experience.picture = pic
            experience.save()
            return self

        def given_a_public_domain(self, public_domain):
            settings.PUBLIC_DOMAIN = public_domain
            return self

        def given_a_dynamic_link(self, dynamic_link):
            settings.DYNAMIC_LINK = dynamic_link
            return self

        def given_a_deep_link_domain(self, deep_link_domain):
            settings.APP_DEEPLINK_DOMAIN = deep_link_domain
            return self

        def when_call_experience_redirect(self, share_id):
            client = Client()
            self.response = client.get(reverse('experience-redirect', args=[share_id]))
            return self

        def then_response_should_be_a_redirect_to(self, url):
            assert self.response.status_code == 302
            assert self.response['Location'] == url
            return self


class RedirectProfileTestCase(TestCase):

    def test_when_there_is_a_dynamic_link_wraps_public_domain_url(self):
        RedirectProfileTestCase.ScenarioMaker() \
                .given_a_profile(username='a_b.c', bio='my info', pic='url') \
                .given_a_public_domain('http://pachatary.com') \
                .given_a_dynamic_link('http://dynamic.link/link={}&other=param') \
                .when_call_profile_redirect('a_b.c') \
                .then_response_should_be_a_redirect_to(
                        'http://dynamic.link/link=http://pachatary.com/p/a_b.c&other=param'
                        '&st=%40a_b.c&sd=my+info&si=%2Fmedia%2Furl.small')

    def test_when_there_is_no_dynamic_link_returns_deep_link(self):
        RedirectProfileTestCase.ScenarioMaker() \
                .given_a_deep_link_domain('pachatary://app') \
                .given_a_dynamic_link('') \
                .when_call_profile_redirect('a_b.c') \
                .then_response_should_be_a_redirect_to('pachatary://app/profiles/a_b.c')

    class ScenarioMaker:

        def given_a_profile(self, username, bio, pic):
            orm_person = ORMPerson.objects.create()
            profile = ORMProfile.objects.create(username=username, bio=bio, person=orm_person)
            profile.picture = pic
            profile.save()
            return self

        def given_a_public_domain(self, public_domain):
            settings.PUBLIC_DOMAIN = public_domain
            return self

        def given_a_dynamic_link(self, dynamic_link):
            settings.DYNAMIC_LINK = dynamic_link
            return self

        def given_a_deep_link_domain(self, deep_link_domain):
            settings.APP_DEEPLINK_DOMAIN = deep_link_domain
            return self

        def when_call_profile_redirect(self, username):
            client = Client()
            self.response = client.get(reverse('profile-redirect', args=[username]))
            return self

        def then_response_should_be_a_redirect_to(self, url):
            assert self.response.status_code == 302
            assert self.response['Location'] == url
            return self


class RedirectRootTestCase(TestCase):

    def test_when_there_is_a_dynamic_link_wraps_public_domain_url(self):
        RedirectRootTestCase.ScenarioMaker() \
                .given_a_public_domain('http://pachatary.com') \
                .given_a_dynamic_link('http://dynamic.link/link={}&other=param') \
                .when_call_root_redirect() \
                .then_response_should_be_a_redirect_to('http://dynamic.link/link=http://pachatary.com/&other=param')

    def test_when_there_is_no_dynamic_link_returns_deep_link(self):
        RedirectRootTestCase.ScenarioMaker() \
                .given_a_deep_link_domain('pachatary://app') \
                .given_a_dynamic_link('') \
                .when_call_root_redirect() \
                .then_response_should_be_a_redirect_to('pachatary://app/')

    class ScenarioMaker:

        def given_a_public_domain(self, public_domain):
            settings.PUBLIC_DOMAIN = public_domain
            return self

        def given_a_dynamic_link(self, dynamic_link):
            settings.DYNAMIC_LINK = dynamic_link
            return self

        def given_a_deep_link_domain(self, deep_link_domain):
            settings.APP_DEEPLINK_DOMAIN = deep_link_domain
            return self

        def when_call_root_redirect(self):
            client = Client()
            self.response = client.get(reverse('root-redirect'))
            return self

        def then_response_should_be_a_redirect_to(self, url):
            assert self.response.status_code == 302
            assert self.response['Location'] == url
            return self


class AASATestCase(TestCase):

    def test_aasa_returns_json_with_appid(self):
        AASATestCase.ScenarioMaker() \
                .given_an_apple_appid('ASDF.com.myapp.ios') \
                .when_call_aasa() \
                .then_response_should_be_json(
                    '{"applinks": {"apps": [], "details": [{"appID": "ASDF.com.myapp.ios", "paths": ["*"]}]}}')

    class ScenarioMaker:

        def given_an_apple_appid(self, appid):
            settings.APPLE_APPID = appid
            return self

        def when_call_aasa(self):
            client = Client()
            self.response = client.get(reverse('aasa'))
            return self

        def then_response_should_be_json(self, json_string):
            assert json.loads(self.response.content) == json.loads(json_string)
            return self
