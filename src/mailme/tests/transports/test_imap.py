import asyncio
import functools

import pytest

from mailme.models import Mailbox
from mailme.transports.imap import ImapTransport, ImapFolder
from mailme.utils.uri import parse_uri
from mailme.tests.imapserver import (
    imap_receive, reset_mailboxes, create_imap_protocol, Mail)


class TestImapTransport:

    @pytest.fixture(autouse=True)
    def setup(self, event_loop, unused_tcp_port):
        self.loop = event_loop
        self.uri = parse_uri('imap://user:pass@127.0.0.1:{}'.format(unused_tcp_port))
        factory = event_loop.create_server(create_imap_protocol, 'localhost', unused_tcp_port)
        self.server = event_loop.run_until_complete(factory)

    def teardown(self):
        reset_mailboxes()
        self.server.close()

    @asyncio.coroutine
    def get_transport(self):
        transport = yield from asyncio.wait_for(
            self.loop.run_in_executor(None, functools.partial(
                ImapTransport, self.uri, Mailbox(provider='custom'))),
            1
        )
        return transport

    @pytest.mark.asyncio
    def test_folders(self):
        imap_receive(Mail(['foo@bar.com'], mail_from='bar@foo.com', content='test'))
        transport = yield from self.get_transport()

        folders = yield from asyncio.wait_for(
            self.loop.run_in_executor(None, transport.folders),
            1
        )

        assert folders == [
            ImapFolder(name='INBOX', role='inbox'),
            ImapFolder(name='INBOX.Archive', role='archive'),
            ImapFolder(name='INBOX.Drafts', role='drafts'),
            ImapFolder(name='INBOX.Sent', role='sent'),
            ImapFolder(name='INBOX.Spam', role=None),
            ImapFolder(name='INBOX.Trash', role='trash')
        ]

    @pytest.mark.asyncio
    def test_folders_to_sync(self):
        transport = yield from self.get_transport()

        folders = yield from asyncio.wait_for(
            self.loop.run_in_executor(None, transport.get_folders_to_sync),
            1
        )

        assert folders == [
            ImapFolder(name='INBOX', role='inbox'),
            ImapFolder(name='INBOX.Archive', role='archive'),
            ImapFolder(name='INBOX.Drafts', role='drafts'),
            ImapFolder(name='INBOX.Sent', role='sent'),
            ImapFolder(name='INBOX.Spam', role=None),
            ImapFolder(name='INBOX.Trash', role='trash')
        ]
