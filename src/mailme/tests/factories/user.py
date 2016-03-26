import factory
from django.contrib.auth.hashers import make_password

from mailme.models import User


class UserFactory(factory.DjangoModelFactory):
    username = factory.Sequence(lambda i: 'user{0}'.format(i))
    is_active = True

    class Meta:
        model = User

    @classmethod
    def _prepare(cls, create, **kwargs):
        raw_password = kwargs.pop('raw_password', 'secret')
        if 'password' not in kwargs:
            kwargs['password'] = make_password(raw_password, hasher='pbkdf2_sha256')
        return super(UserFactory, cls)._prepare(create, **kwargs)
