import ssl
import urllib
from urllib.parse import urlencode, urljoin

import pkg_resources
import requests
from requests_toolbelt import SSLAdapter, user_agent

from mailme.utils.http import InsecureTransport, InvalidHost, is_secure_transport, verify_host


class TLS12SSLAdapter(SSLAdapter):

    def __init__(self, *args, **kwargs):
        kwargs['ssl_version'] = ssl.PROTOCOL_TLSv1_2
        super(TLS12SSLAdapter, self).__init__(**kwargs)


class APIError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

    def __repr__(self):
        return f'<APIError({self.message})>'


class Client(requests.Session):
    """Proof of concept client implementation."""
    content_type = 'application/vnd.mailme+json'

    host = 'mailme.io'
    port = '443'
    timeout = 3.0
    force_https = True

    def __init__(self, jwt_token=None):
        super(Client, self).__init__()

        self.mount('https://', TLS12SSLAdapter())
        self.jwt_token = jwt_token

    def build_url(self, endpoint, qs=None):
        scheme = 'https' if self.force_https else 'http'
        url = urljoin(f'{scheme}://{self.host}:{self.port}', endpoint)

        if qs:
            url += '?' + urlencode(qs)
        return url

    def request(self, method, url, *args, **kwargs):
        if self.force_https and not is_secure_transport(url):
            raise InsecureTransport('Please make sure to use HTTPS')

        if not verify_host(url, [self.host]):
            raise InvalidHost(
                f'Please verify the client is using '
                f'"{self.host}" has host')

        parse_result = urllib.parse.urlparse(url)

        dist = pkg_resources.get_distribution('mailme')

        headers = {
            'User-Agent': user_agent('mailme', dist.version),
            'Host': parse_result.netloc,
            'Method': method,
            'Path': parse_result.path,
            'Accept': self.content_type,
            'Content-Type': self.content_type,
        }

        if self.jwt_token:
            headers['Authorization'] = f'JWT {self.jwt_token}'

        headers.update(kwargs.pop('headers', {}))

        kwargs.update({
            'headers': headers,
            'timeout': self.timeout,
        })

        return super(Client, self).request(method, url, *args, **kwargs)

    def _api_request(self, method, *args, **kwargs):
        try:
            response = self.request(method, *args, **kwargs)
        except requests.HTTPError as exc:
            msg = 'lalalal'

            if msg:
                raise APIError(msg)
            else:
                raise exc

        return response

    def register(self, username, password):
        """Register a new user"""
        url = self.build_url('/api/auth/register/')
        response = self._api_request('POST', url, json={
            'username': username,
            'password': password
        })
        if response.status_code == 400:
            raise APIError(response.content.decode())

        assert response.status_code == 201
        return response


class LocalClient(Client):
    host = 'localhost'
    port = '8000'
    force_https = False
