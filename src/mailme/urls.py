from django.conf.urls import include, url
from django.contrib import admin


urlpatterns = [
    # Hookup our REST Api
    url(r'^api/', include('mailme.api.urls', namespace='api')),
    url(r'^api/docs/', include('rest_framework.urls', namespace='rest_framework')),

    # Admin
    url(r'^admin/', include(admin.site.urls)),
]
