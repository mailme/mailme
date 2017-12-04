from django.urls import include, path
from django.contrib import admin


urlpatterns = [
    path('api/', include(('mailme.api.urls', 'api'), namespace='api')),
    path('api/docs/', include('rest_framework.urls')),

    # Admin
    path('admin/', admin.site.urls),
]
