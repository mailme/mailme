import os
import email

from django.conf import settings

from mailme.utils.parser import parse_email, get_mail_addresses
from mailme.tests.utils.samples import generate_parameters, SAMPLE_MAILS


class TestParser:

    def open_mail(self, name):
        path = os.path.join(settings.BASE_DIR, 'tests', 'resources', 'mails', name)

        with open(path, 'r') as fobj:
            content = fobj.read()

        return content

    def test_original_is_string(self):
        raw = self.open_mail('simple.txt')
        parsed = parse_email(raw)

        assert isinstance(parsed['original'], str)

    @generate_parameters(SAMPLE_MAILS)
    def test_simple(self, file, expected):
        raw = self.open_mail(file)
        parsed = parse_email(raw)
        assert parsed == expected
        assert isinstance(parsed['original'], str)

    def test_parse_email_case_insensitive_header(self):
        assert parse_email('Message-ID: one')['message_id'] == 'one'
        assert parse_email('Message-Id: one')['message_id'] == 'one'
        assert parse_email('Message-id: one')['message_id'] == 'one'
        assert parse_email('message-id: one')['message_id'] == 'one'

    def test_get_mail_addresses(self):
        to_address = email.message_from_string('To: John Doe <johndoe@gmail.com>')
        from_address = email.message_from_string('From: John Smith <johnsmith@gmail.com>')

        assert get_mail_addresses(to_address, 'to') == [{
            'email': 'johndoe@gmail.com', 'name': 'John Doe'
        }]

        assert get_mail_addresses(from_address, 'from') == [{
            'email': 'johnsmith@gmail.com', 'name': 'John Smith'
        }]
