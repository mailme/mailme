import pytest

from mailme.models import User
from mailme.tests.factories.user import UserFactory


@pytest.mark.django_db
class TestUserModel:

    def setup(self):
        self.user = UserFactory.create()

    def test_short_name(self):
        assert self.user.get_short_name() == self.user.username

    def test_check_password(self):
        user = User()
        user.set_password('test')
        assert user.check_password('test')

    def test_check_password_unicode(self):
        user = User()
        user.set_password('winter is coming ☃❄')
        assert user.check_password('winter is coming ☃❄')
