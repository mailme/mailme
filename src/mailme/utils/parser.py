# Loosely based on imbox <https://github.com/martinrusev/imbox>
import io
import re
import email
import base64
import quopri
from email.header import decode_header

import chardet
from django.utils.encoding import force_text, force_bytes


RE_PARAM = re.compile(r'=\?((?:\w|-)+)\?(Q|B)\?(.+)\?=')


def decode_mail_header(value, default_charset='us-ascii'):
    """
    Decode a header value into a unicode string.
    """
    try:
        headers = decode_header(value)
    except email.errors.HeaderParseError:
        return force_text(value)

    for index, (text, charset) in enumerate(headers):
        try:
            headers[index] = force_text(text, errors='replace')
        except LookupError:
            # if the charset is unknown, force default
            headers[index] = force_text(text, default_charset, errors='replace')

    return ''.join(headers)


def get_mail_addresses(message, header_name):
    """
    Retrieve all email addresses from one message header.
    """
    headers = [h for h in message.get_all(header_name, [])]
    addresses = email.utils.getaddresses(headers)

    for index, (address_name, address_email) in enumerate(addresses):
        addresses[index] = {
            'name': decode_mail_header(address_name),
            'email': address_email
        }

    return addresses


def decode_param(param):
    name, v = param.split('=', 1)
    values = v.split('\n')
    value_results = []

    for value in values:
        match = re.search(RE_PARAM, value)

        if match:
            encoding, type_, code = match.groups()

            if type_ == 'Q':
                value = quopri.decodestring(code)
            elif type_ == 'B':
                value = base64.decodestring(code)

            value = force_bytes(value, encoding)
            value_results.append(value)

            if value_results:
                v = ''.join(value_results)
    return name, v


def parse_attachment(message_part):
    # Check again if this is a valid attachment
    content_disposition = message_part.get('Content-Disposition', None)
    if content_disposition is not None and not message_part.is_multipart():
        dispositions = content_disposition.strip().split(';')

        if dispositions[0].lower() in ['attachment', 'inline']:
            file_data = message_part.get_payload(decode=True)

            attachment = {
                'content-type': message_part.get_content_type(),
                'size': len(file_data),
                'content': io.BytesIO(file_data)
            }
            filename = message_part.get_param('name')
            if filename:
                attachment['filename'] = filename

            for param in dispositions[1:]:
                name, value = decode_param(param)

                if 'file' in name:
                    attachment['filename'] = value

                if 'create-date' in name:
                    attachment['create-date'] = value

            return attachment

    return None


def decode_content(message):
    content = message.get_payload(decode=True)
    charset = message.get_content_charset('utf-8')
    try:
        return content.decode(charset)
    except UnicodeDecodeError:
        # Scenarios like no-breaking space in utf-8 which should be latin-1
        # encoding :-/
        charset = chardet.detect(content)
        return content.decode(charset['encoding'])
    except AttributeError:
        return content


def parse_email(raw_email):
    if isinstance(raw_email, bytes):
        try:
            raw_email = force_text(raw_email)
        except UnicodeDecodeError:
            raw_email = raw_email.decode(chardet.detect(raw_email)['encoding'])

    message = email.message_from_string(raw_email)
    maintype = message.get_content_maintype()

    parsed_email = {'original': raw_email}

    body = {
        'plain': [],
        'html': []
    }
    attachments = []

    if maintype in ('multipart', 'image'):
        for part in message.walk():
            content_type = part.get_content_type()
            part_maintype = part.get_content_maintype()
            content_disposition = part.get('Content-Disposition', None)

            if content_disposition or not part_maintype == 'text':
                content = part.get_payload(decode=True)
            else:
                content = decode_content(part)

            is_inline = content_disposition is None or content_disposition == 'inline'

            if content_type == 'text/plain' and is_inline:
                body['plain'].append(content)
            elif content_type == 'text/html' and is_inline:
                body['html'].append(content)
            elif content_disposition:
                attachment = parse_attachment(part)
                if attachment:
                    attachments.append(attachment)

    elif maintype == 'text':
        payload = decode_content(message)
        body['plain'].append(payload)

    parsed_email['attachments'] = attachments

    parsed_email['body'] = body
    email_dict = dict(message.items())

    parsed_email['sent_from'] = get_mail_addresses(message, 'from')
    parsed_email['sent_to'] = get_mail_addresses(message, 'to')
    parsed_email['cc'] = get_mail_addresses(message, 'cc')
    parsed_email['bcc'] = get_mail_addresses(message, 'bcc')

    value_headers_keys = {'subject', 'date', 'message-id'}
    key_value_header_keys = {
        'received-spf', 'mime-version', 'x-spam-status', 'x-spam-score',
        'content-type'
    }

    parsed_email['headers'] = {}

    for key, value in email_dict.items():
        if key.lower() in value_headers_keys:
            valid_key_name = key.lower().replace('-', '_')
            parsed_email[valid_key_name] = decode_mail_header(value)

        if key.lower() in key_value_header_keys:
            parsed_email['headers'][key.lower()] = value

    if parsed_email.get('date'):
        parsed_email['parsed_date'] = email.utils.parsedate_to_datetime(parsed_email['date'])

    return parsed_email
