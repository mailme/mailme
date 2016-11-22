import factory

from mailme.models import Mailbox
from mailme.tests.factories.user import UserFactory


class MailboxFactory(factory.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    name = 'custom'
    provider = 'custom'

    class Meta:
        model = Mailbox
