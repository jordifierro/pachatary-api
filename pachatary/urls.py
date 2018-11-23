from django.conf.urls import url
from django.http import HttpResponse
from django.urls import include, path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView

from .views import client_versions, privacy_policy, terms_and_conditions, aasa_redirect

app_name = 'pachatary'
urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^experiences/', include('experiences.urls')),

    url(r'^scenes/', include('scenes.urls')),

    url(r'^people/', include('people.urls')),

    url(r'^profiles/', include('profiles.urls')),

    url(r'^', include('redirects.urls')),


    url(r'^$', RedirectView.as_view(url=settings.LANDING_URL, permanent=False), name='index'),
    url(r'^client-versions$', client_versions, name='client-versions'),
    url(r'^apple-app-site-association$', aasa_redirect, name='aasa'),
    url(r'^privacy-policy$', privacy_policy, name='privacy-policy'),
    url(r'^terms-and-conditions$', terms_and_conditions, name='terms-and-conditions'),
    url(r'^robots.txt$', lambda r: HttpResponse('User-agent: *\nDisallow: /', content_type='text/plain'))
]

if settings.LOCAL_DEPLOY:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [path('django-rq/', include('django_rq.urls'))]
