from collections import namedtuple
from email.errors import MessageParseError

from django.db.models import Max
from imapclient import IMAPClient

from .base import EmailTransport
from mailme.constants import DEFAULT_FOLDER_FLAGS, DEFAULT_FOLDER_MAPPING
from mailme.providers import get_provider_info


DEFAULT_POLL_FREQUENCY = 30

ImapFolder = namedtuple('ImapFolder', ('name', 'role'))


class ImapTransport(EmailTransport):
    def __init__(self, uri, provider):
        self.uri = uri
        self.provider_info = get_provider_info(provider)
        self._server = None

    def connect(self):
        server = IMAPClient(self.uri.location, use_uid=True, ssl=self.uri.use_ssl)
        server.login(self.uri.username, self.uri.password)
        return server

    @property
    def server(self):
        if self._server is None:
            self._server = self.connect()
        return self._server

    def get_new_uids(self):
        lastseenuid = Message.objects.aggregate(max_uid=Max('uid'))['max_uid'] or 0

        new_messages = self.server.fetch('{}:*'.format(lastseenuid + 1), ['UID'])
        # tag2 UID FETCH 1:<lastseenuid> FLAGS

    def folders(self):
        """Fetch the list of folders for the account from the remote."""
        ignore = {'\\Noselect', '\\NoSelect', '\\NonExistent'}
        provider_map = self.provider_info.get('folder_map', {})
        _folder_list = self.server.list_folders()

        retval = []

        for flags, delimiter, name in _folder_list:
            if name in ignore:
                # Special folders that can't contain messages
                continue

            role = DEFAULT_FOLDER_MAPPING.get(name.lower(), None)

            if role is None:
                role = provider_map.get(name, None)

            if role is None:
                # Try to figure out the correct folder by looking
                # into flags
                for flag in flags:
                    role = DEFAULT_FOLDER_FLAGS.get(flag)

            retval.append(ImapFolder(name=name, role=role))

        return retval
