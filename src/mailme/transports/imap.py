import imaplib
import ssl
from collections import namedtuple, OrderedDict

from django.db.models import Max
from imapclient import IMAPClient

from .base import EmailTransport
from mailme.constants import (
    DEFAULT_FOLDER_FLAGS, DEFAULT_FOLDER_MAPPING, IGNORE_FOLDER_NAMES
)
from mailme.providers import get_provider_info
from mailme.utils.uri import parse_uri


DEFAULT_POLL_FREQUENCY = 30
imaplib.Debug = 4

ImapFolder = namedtuple('ImapFolder', ('name', 'role'))


class ImapTransport(EmailTransport):
    def __init__(self, uri, mailbox, disable_cert_check=False):
        if isinstance(uri, str):
            self.uri = parse_uri(uri)

        self.mailbox = mailbox
        self.provider_info = get_provider_info(mailbox.provider)
        self._client = None
        self._disable_cert_check = disable_cert_check

    def connect(self):
        kwargs = {}

        if self._disable_cert_check:
            ssl_context = ssl.create_default_context()

            # don't check if certificate hostname doesn't match target hostname
            ssl_context.check_hostname = False

            # don't check if the certificate is trusted by a certificate authority
            ssl_context.verify_mode = ssl.CERT_NONE

            kwargs['ssl_context'] = ssl_context

        client = IMAPClient(
            self.uri.location,
            self.uri.port if self.uri.port else None,
            use_uid=True,
            ssl=self.uri.use_ssl,
            **kwargs)

        if self.uri.use_tls:
            client.starttls()

        # TODO: Check for condstore and enable
        # if client.has_capability('ENABLE') and client.has_capability('CONDSTORE'):
        #       client.enable('CONDSTORE')
        #       condstore_enabled = True

        client.login(self.uri.username, self.uri.password)
        return client

    @property
    def client(self):
        if self._client is None:
            self._client = self.connect()
        return self._client

    def sync(self):
        for imap_folder in self.get_folders_to_sync():
            # TODO: normalize folder name? role isn't specific enough imho
            # but maybe it is and should be used for normalization?
            folder, _ = self.mailbox.folders.get_or_create(name=imap_folder.name)
            lastseenuid = folder.messages.aggregate(max_uid=Max('uid'))['max_uid'] or 0

            # Begin imap session, please note that `self.client` isn't stateless
            # but all following actions are executed against the actual folder
            self.client.select_folder(folder.name, readonly=True)

            folder_status = self.client.folder_status(
                folder.name, ['UIDNEXT', 'UIDVALIDITY'])

            # TODO: Evaluate `highestmodseq`
            need_sync = (
                folder.uidnext != folder_status[b'UIDNEXT'] and
                folder.uidvalidity != folder_status[b'UIDVALIDITY'])

            if not need_sync:
                continue

            # TODO:
            # if folder.uidvalidity != folder_status[b'UIDVALIDITY']:
            #     # full resync

            new_message_uids = self.client.fetch(
                f'{lastseenuid + 1}:*',
                (
                    'FLAGS', 'UID', 'BODYSTRUCTURE', 'INTERNALDATE',
                    'RFC822.SIZE'
                )
            )

            print(new_message_uids)

            message_id_batch = self.uid_sequence(new_message_uids.keys())

            print('fetching', message_id_batch)

            # TODO:
            # Add support for GMail specific flags: X-GM-THRID, X-GM-MSGID,
            # X-GM-LABELS
            data = self.client.fetch(
                message_id_batch,
                ('BODY.PEEK[]',)
            )

            for uid, msg in data.items():
                print(self.get_email_from_bytes(msg[b'BODY[]']))

            # We're done with the update, mark the new state in the database
            self.mailbox.folders.filter(name=imap_folder.name).update(
                uidnext=folder_status[b'UIDNEXT'],
                uidvalidity=folder_status[b'UIDVALIDITY']
            )

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
        provider_map = self.provider_info.get('folder_map', {})
        _folder_list = self.client.list_folders()

        retval = []

        for flags, delimiter, name in _folder_list:
            if name in IGNORE_FOLDER_NAMES:
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

    def uid_sequence(self, uidlist):
        """Collapse UID lists into shorter sequence sets

        E.g [1,2,3,4,5,10,12,13] will return "1:5,10,12:13".

        This function sorts the list, and only collapses if subsequent entries
        form a range.

        :returns: The collapsed UID list as string.
        """

        def getrange(start, end):
            if start == end:
                return str(start)
            return f'{start}:{end}'

        if not uidlist:
            return ''

        start, end = None, None
        retval = []

        # Force items to be longs and sort them
        sorted_uids = sorted(map(int, uidlist))

        for item in sorted_uids:
            item = int(item)
            if start is None:
                # first item
                start, end = item, item
            elif item == end + 1:
                # Next item in a range
                end = item
            else:
                # Starting a new range
                retval.append(getrange(start, end))
                start, end = item, item

        # Add final range/item
        retval.append(getrange(start, end))
        return ','.join(retval)
