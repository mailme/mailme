from mailme.utils.parser import parse_email


class EmailTransport(object):
    def get_email_from_bytes(self, contents):
        return parse_email(contents)
