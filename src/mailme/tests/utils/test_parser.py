import os
import email

from django.conf import settings

from mailme.utils.parser import parse_email, get_mail_addresses


# TODO
# Reply-To :  Sam.Irving@Reg.Organization
# To       :  George Jones <Group@Some-Reg.An-Org>,
#             Al.Neuman@MAD.Publisher
# cc       :  Important folk:
#               Tom Softwood <Balsa@Tree.Root>,
#               "Sam Irving"@Other-Host;,
#             Standard Distribution:
#               /main/davis/people/standard@Other-Host,
#               "<Jones>standard.dist.3"@Tops-20-Host>;
# Comment  :  Sam is away on business. He asked me to handle
#             his mail for him.  He'll be able to provide  a
#             more  accurate  explanation  when  he  returns
#             next week.
# In-Reply-To: <some.string@DBM.Group>, George's message

# TODO (already works, needs tests):
# In [4]: parsedate_to_datetime("Mon, 20 Nov 1995 19:12:08 -0500")
# Out[4]: datetime.datetime(
#   1995, 11, 20, 19, 12, 8, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))

# In [5]: parsedate_to_datetime("Mon, 20 Nov 1995 19:12:08")
# Out[5]: datetime.datetime(1995, 11, 20, 19, 12, 8)

# In [6]: parsedate_to_datetime("Mon, 20 Nov 1995 19:12:08 -0000")
# Out[6]: datetime.datetime(1995, 11, 20, 19, 12, 8)


class TestParser:

    def open_mail(self, name):
        path = os.path.join(settings.BASE_DIR, 'tests', 'resources', 'mails', name)

        with open(path, 'r') as fobj:
            content = fobj.read()

        return content

    def test_simple(self):
        raw = self.open_mail('simple.txt')
        parsed = parse_email(raw)

        assert isinstance(parsed['original'], str)
        assert parsed['original'] == raw
        assert parsed['subject'] == 'Test email - no attachment'
        assert parsed['date'] == 'Tue, 30 Jul 2013 15:56:29 +0300'
        assert parsed['message_id'] == '<test0@example.com>'

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
