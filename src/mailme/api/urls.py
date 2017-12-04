from django.urls import path

from .endpoints.dummy import AuthenticatedDummyView
from .endpoints.auth import RegisterView, LoginView


urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),

    # Dummy view, used for testing.
    path('dummy/', AuthenticatedDummyView.as_view()),
]
