import pytest
from django.core.urlresolvers import reverse

from mailme.models import User
from mailme.utils.test import APIClient


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
            'username': 'testuser',
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
