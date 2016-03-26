import mock
import pytest
from django.core.urlresolvers import reverse

from mailme.models import User
from mailme.utils.test import APIClient

from mailme.tests.factories.user import UserFactory


@pytest.mark.django_db
class TestRegistration:

    def test_simple_register(self):
        url = reverse('api:register')

        response = APIClient().post(url, data={
            'username': 'testuser',
            'password': 'test123456',
        })

        assert response.status_code == 201
        assert response.json() == {
            'user': {
                'username': 'testuser',
                'name': None,
            },
            'token': mock.ANY,
        }
        assert User.objects.filter(username='testuser').exists()

    def test_register_invalid_password(self):
        url = reverse('api:register')

        response = APIClient().post(url, data={
            'username': 'testuser',
            'password': '1234',
        })

        assert response.status_code == 400
        assert response.json() == {
            'password': [
                'This password is too short. It must contain at least 10 characters.',
                'This password is too common.',
                'This password is entirely numeric.'
            ]
        }

        # Make sure we never created a user or device
        assert User.objects.all().count() == 0

    def test_register_invalid_username_unique(self):
        url = reverse('api:register')

        User.objects.create(username='testuser')
        response = APIClient().post(url, data={
            'username': 'testuser',
            'password': 'test123456',
        })

        assert response.status_code == 400
        assert response.json() == {
            'username': ['User with this Username already exists.']
        }


@pytest.mark.django_db
class TestLogin:
    def setup(self):
        self.user = UserFactory.create(username='testuser', raw_password='test123456')
        self.url = reverse('api:login')

    def test_simple_login(self):
        response = APIClient().post(self.url, data={
            'username': 'testuser',
            'password': 'test123456',
        })

        assert response.status_code == 200
        print(response.json())

    def test_register_invalid_password(self):
        response = APIClient().post(self.url, data={
            'username': 'testuser',
            'password': '1234',
        })

        assert response.status_code == 400
        assert response.json() == {
            'non_field_errors': ['Unable to log in with provided credentials.']
        }
