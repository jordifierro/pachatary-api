from django.conf.urls import url
from django.urls import include, path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from .views import client_versions, privacy_policy, terms_and_conditions

app_name = 'pachatary'
urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^experiences/', include('experiences.urls')),

    url(r'^scenes/', include('scenes.urls')),

    url(r'^people/', include('people.urls')),

    url(r'^profiles/', include('profiles.urls')),

    url(r'^', include('redirects.urls')),

    url(r'^client-versions$', client_versions, name='client-versions'),
    url(r'^privacy-policy$', privacy_policy, name='privacy-policy'),
    url(r'^terms-and-conditions$', terms_and_conditions, name='terms-and-conditions'),
]

if settings.LOCAL_DEPLOY:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [path('django-rq/', include('django_rq.urls'))]
