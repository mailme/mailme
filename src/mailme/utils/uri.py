from collections import namedtuple
from urllib.parse import parse_qs, unquote, urlparse


URI = namedtuple('URI', (
    'protocol_info', 'query_string', 'domain', 'port', 'username', 'password',
    'location', 'scheme', 'use_ssl'
))

def parse_uri(uri):
    protocol_info = urlparse(uri)
    scheme = protocol_info.scheme.lower()

    if '+' in scheme:
        scheme = scheme.split('+')[0]

    return URI(
        protocol_info=protocol_info,
        query_string=parse_qs(protocol_info.query),
        domain=protocol_info.hostname,
        port=protocol_info.port,
        username=unquote(protocol_info.username),
        password=unquote(protocol_info.password),
        location=protocol_info.hostname if protocol_info.hostname else '' + protocol_info.path,
        scheme=scheme,
        use_ssl='+ssl' in protocol_info.scheme.lower()
    )
