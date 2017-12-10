import uuid

import factory
from django.contrib.auth.hashers import make_password

from mailme.models import User


def _generate_username(idx):
    hash = str(uuid.uuid4()).split('-')[0]
    return f'user-{hash}'


class UserFactory(factory.DjangoModelFactory):
    username = factory.Sequence(_generate_username)
    is_active = True

    class Meta:
        model = User

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override the default _create() to disable the post-save signal."""
        raw_password = kwargs.pop('raw_password', 'secret')
        if 'password' not in kwargs:
            kwargs['password'] = make_password(raw_password, hasher='pbkdf2_sha256')

        user = super(UserFactory, cls)._create(model_class, *args, **kwargs)
        return user
