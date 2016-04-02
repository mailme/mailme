import asyncio
import functools

import pytest

from mailme.transports.imap import ImapTransport
from mailme.utils.uri import parse_uri
from mailme.tests.imapserver import (
    imap_receive, reset_mailboxes, create_imap_protocol, Mail)


class TestImapTransport:

    @pytest.fixture(autouse=True)
    def setup(self, unused_tcp_port, event_loop):
        self.loop = event_loop
        factory = self.loop.create_server(
            create_imap_protocol(),
            'localhost',
            unused_tcp_port
        )
        self.server = self.loop.run_until_complete(factory)
        asyncio.sleep(2)
        self.uri = parse_uri('imap://user:pass@127.0.0.1:{}'.format(unused_tcp_port))

    @asyncio.coroutine
    def teardown(self):
        reset_mailboxes()
        self.server.close()
        asyncio.wait_for(self.server.wait_closed(), 1)

    @asyncio.coroutine
    def run_async(self, loop, uri, login, password, func, *args, **kwargs):
        transport = ImapTransport(uri, 'custom')

        args = (transport,) + args

        result = yield from asyncio.wait_for(loop.run_in_executor(
            None, functools.partial(func, *args, **kwargs)
        ), 10)

        return result

    @pytest.mark.asyncio
    def test_folders(self):
        imap_receive(Mail(['foo@bar.com'], mail_from='bar@foo.com', content='test'))

        def _test(transport):
            folders = transport.folders()
            import ipdb; ipdb.set_trace()
            assert folders == []

        result = yield from self.run_async(self.loop, self.uri, 'user', 'pass', _test)
