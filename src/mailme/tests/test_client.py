import pytest
from urllib3.util.url import parse_url

from mailme.client import LocalClient
from mailme.models import User
from mailme.tests.factories.user import UserFactory


@pytest.mark.django_db(transaction=True)
class TestTestClient:

    @pytest.fixture(autouse=True)
    def setup(self, settings, live_server):
        self.liveserver = live_server

    def get_client(self, jwt_token=None):
        client = LocalClient(jwt_token)
        parsed_url = parse_url(self.liveserver.url)
        client.host = parsed_url.host
        client.port = parsed_url.port
        return client

    def test_simple_unauthorized(self):
        UserFactory.create()

        client = self.get_client()

        endpoint = '{0}/api/dummy/'.format(self.liveserver.url)

        response = client.get(endpoint)

        assert response.status_code == 401

    def test_register(self):
        client = self.get_client()
        client.register('testuser', 'test123456')

        assert User.objects.filter(username='testuser').exists()
