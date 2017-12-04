import pytest

from mailme.transports.imap import ImapTransport
from mailme.tests.factories.mailbox import MailboxFactory


@pytest.mark.django_db
class TestImapTransport:

    def get_transport(self):
        mailbox = MailboxFactory.create()
        print('created mailbox')
        transport = ImapTransport(self.uri, mailbox)
        print('created transport')
        return transport
