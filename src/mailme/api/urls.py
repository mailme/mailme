from django.conf.urls import url

from .endpoints.dummy import AuthenticatedDummyView
from .endpoints.auth import RegisterView, LoginView


urlpatterns = [
    url(r'auth/register/$', RegisterView.as_view(), name='register'),
    url(r'auth/login/$', LoginView.as_view(), name='login'),

    # Dummy view, used for testing.
    url(r'dummy/$', AuthenticatedDummyView.as_view()),
]
