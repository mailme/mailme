import os
import datetime

import pytest
import mock
from django.conf import settings


def _read(name):
    path = os.path.join(settings.BASE_DIR, 'tests', 'resources', 'mails', name)

    with open(path, 'r') as fobj:
        content = fobj.read()

    return content


def generate_parameters(source):
    keys = source['keys']
    return pytest.mark.parametrize(keys, [
        tuple([entry[k] for k in keys])
        for entry in source['samples']
    ])


SAMPLE_MAILS = {
    'keys': ('file', 'expected'),
    'samples': [
        {
            'file': 'generic.txt',
            'expected': {
                'original': _read('generic.txt'),
                'parsed_date': datetime.datetime(
                    2013, 1, 20, 11, 53, 53,
                    tzinfo=datetime.timezone(datetime.timedelta(hours=-8))),
                'date': 'Sun, 20 Jan 2013 11:53:53 -0800',
                'message_id': '<CAMdmm+hGH8Dgn-_0xnXJCd=PhyNAiouOYm5zFP0z-foqTO60zA@mail.gmail.com>',
                'subject': 'Message Without Attachment',
                'cc': [],
                'bcc': [],
                'from': [{'name': 'Adam Coddington', 'email': 'test@adamcoddington.net'}],
                'to': [{'name': 'Adam Coddington', 'email': 'test@adamcoddington.net'}],
                'body': {'plain': ['Hello there.\n'], 'html': []},
                'headers': {
                    'content-type': 'text/plain; charset="iso-8859-1"',
                    'mime-version': '1.0'
                },
                'attachments': [],
            },
        }
    ]
}
