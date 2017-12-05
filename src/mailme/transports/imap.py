import imaplib
from collections import namedtuple, OrderedDict

from django.db.models import Max
from imapclient import IMAPClient

from .base import EmailTransport
from mailme.constants import DEFAULT_FOLDER_FLAGS, DEFAULT_FOLDER_MAPPING
from mailme.providers import get_provider_info


DEFAULT_POLL_FREQUENCY = 30
imaplib.Debug = 4

ImapFolder = namedtuple('ImapFolder', ('name', 'role'))


class ImapTransport(EmailTransport):
    def __init__(self, uri, mailbox):
        self.uri = uri
        self.mailbox = mailbox
        self.provider_info = get_provider_info(mailbox.provider)
        self._server = None

    def connect(self):
        server = IMAPClient(
            self.uri.location,
            self.uri.port if self.uri.port else None,
            use_uid=True,
            ssl=self.uri.use_ssl)

        if self.uri.use_tls:
            self.server.starttls()

        # TODO: Check for condstore and enable
        # if client.has_capability('ENABLE') and client.has_capability('CONDSTORE'):
        #       client.enable('CONDSTORE')
        #       condstore_enabled = True

        response = server.login(self.uri.username, self.uri.password)
        return server

    @property
    def server(self):
        if self._server is None:
            self._server = self.connect()
        return self._server

    def sync(self):
        # TODO: This should absolutely be asyncronous and
        # push out one task per folder or something smarter
        for imap_folder in self.get_folders_to_sync():
            # TODO: normalize folder name? role isn't specific enough imho
            # but maybe it is and should be used for normalization?
            folder = self.mailbox.folders.get_or_create(name=imap_folder.name)
            lastseenuid = folder.aggregate(max_uid=Max('uid'))['max_uid'] or 0

            # Begin imap session, please note that `self.server` isn't stateless
            # but all following actions are executed against the actual folder
            self.server.select_folder(folder.name)

            folder_status = self.server.folder_status(folder, ['UIDNEXT', 'UIDVALIDITY'])

            new_messages = self.server.fetch('{}:*'.format(lastseenuid + 1), ['UID'])

            print(folder_status, new_messages)

        # tag2 UID FETCH 1:<lastseenuid> FLAGS

    def get_folders_to_sync(self):
        to_sync = []
        folders = self.folders()

        _folder_names = OrderedDict()

        # TODO: prioritize properly
        for folder in folders:
            _folder_names.setdefault(folder.role, [])
            _folder_names[folder.role].append(folder)

        # TODO: for gmail make sure that we only sync `all`, `spam` and `trash`.
        # Sync `inbox` folder first, then others.
        to_sync = _folder_names['inbox']
        for role, folders in _folder_names.items():
            if role == 'inbox':
                continue
            to_sync.extend(folders)

        return to_sync

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
