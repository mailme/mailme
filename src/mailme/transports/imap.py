import imaplib
from collections import namedtuple, defaultdict

from django.db.models import Max
from imapclient import IMAPClient

from .base import EmailTransport
from mailme.models import Message
from mailme.constants import DEFAULT_FOLDER_FLAGS, DEFAULT_FOLDER_MAPPING
from mailme.providers import get_provider_info


DEFAULT_POLL_FREQUENCY = 30
imaplib.Debug = 4

ImapFolder = namedtuple('ImapFolder', ('name', 'role'))


class ImapTransport(EmailTransport):
    def __init__(self, uri, provider):
        self.uri = uri
        self.provider_info = get_provider_info(provider)
        self._server = None

    def connect(self):
        print(self.uri, self.uri.port)
        server = IMAPClient(
            self.uri.location,
            self.uri.port if self.uri.port else None,
            use_uid=True,
            ssl=self.uri.use_ssl)
        response = server.login(self.uri.username, self.uri.password)
        print(response)
        # TODO: grab capabilities list (but not everyone provides it):
        # b'[CAPABILITY IMAP4rev1 LITERAL+ ID ENABLE XAPPLEPUSHSERVICE ACL
        #    RIGHTS=kxten QUOTA MAILBOX-REFERRALS NAMESPACE UIDPLUS
        #    NO_ATOMIC_RENAME UNSELECT CHILDREN MULTIAPPEND BINARY
        #    CATENATE CONDSTORE ESEARCH SEARCH=FUZZY SORT SORT=MODSEQ
        #    SORT=DISPLAY SORT=UID THREAD=ORDEREDSUBJECT...
        return server

    @property
    def server(self):
        if self._server is None:
            self._server = self.connect()
        return self._server

    def sync(self):
        for folder in self.get_folders_to_sync():
            self.server.select_folder(folder)

            lastseenuid = (Message.objects
                .filter(folder__name=folder)
                .aggregate(max_uid=Max('uid'))['max_uid'] or 0)

            folder_status = self.server.folder_status(folder, ['UIDNEXT', 'UIDVALIDITY'])

            new_messages = self.server.fetch('{}:*'.format(lastseenuid + 1), ['UID'])

            print(folder_status, new_messages)

        # tag2 UID FETCH 1:<lastseenuid> FLAGS

    def get_folders_to_sync(self):
        to_sync = []
        folders = self.folders()

        _folder_names = defaultdict(list)

        for folder in folders:
            _folder_names[folder.role].append(folder.name)

        # Sync inbox folder first, then others.
        to_sync = _folder_names['inbox']
        for role, folder_names in _folder_names.items():
            if role == 'inbox':
                continue
            to_sync.extend(folder_names)

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
