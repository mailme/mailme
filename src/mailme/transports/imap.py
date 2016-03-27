import imaplib
from email.errors import MessageParseError

from .base import EmailTransport


# By default, imaplib will raise an exception if it encounters more
# than 10k bytes; sometimes users attempt to consume mailboxes that
# have a more, and modern computers are skookum-enough to handle just
# a *few* more messages without causing any sort of problem.
imaplib._MAXLINE = 1000000
imaplib.Debug = 4


class ImapTransport(EmailTransport):
    max_message_size = None

    def __init__(self, hostname, port=None, ssl=False):
        self.hostname = hostname
        self.port = port

        if ssl:
            self.transport = imaplib.IMAP4_SSL
            if not self.port:
                self.port = 993
        else:
            self.transport = imaplib.IMAP4
            if not self.port:
                self.port = 143

    def connect(self, username, password):
        self.connection = self.transport(self.hostname, self.port)
        typ, msg = self.connection.login(username, password)

        self.connection.select()

    def _get_all_message_ids(self, **query):
        query = self.build_search_query(**query)

        # Fetch all the message uids
        response, message_ids = self.connection.uid('search', None, query)
        message_id_string = message_ids[0].strip()

        # Usually `message_id_string` will be a list of space-separated
        # ids; we must make sure that it isn't an empty string before
        # splitting into individual UIDs.
        if message_id_string:
            return message_id_string.decode().split(' ')
        return []

    def get_messages(self, condition=None, folder=None, **query):
        message_ids = self._get_all_message_ids(**query)

        if not message_ids:
            return

        for uid in message_ids:
            try:
                message, data = self.connection.uid('fetch', uid, '(BODY.PEEK[])')
                raw_email = data[0][1]

                if not raw_email:
                    continue

                yield self.get_email_from_bytes(raw_email)
            except MessageParseError:
                continue
        return

    def folders(self):
        return self.connection.list()

    def build_search_query(self, **kwargs):
        mapping = {
            'sent_from': '(FROM "{}")',
            'sent_to': '(TO "{}")',
            'subject': '(SUBJECT "{}")'
        }

        query = []

        if kwargs.pop('unread', False):
            query.append('(UNSEEN)')

        for key, value in mapping.items():
            search_string = kwargs.pop(key, None)

            if search_string:
                query.append(value.format(search_string))

        if query:
            return ' '.join(query)

        return '(ALL)'
