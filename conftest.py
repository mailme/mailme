import os
import os.path

import requests
import pytest
from django.conf import settings as django_settings
from pytest_django.lazy_django import skip_if_no_django


def pytest_configure(config):
    if not django_settings.configured:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mailme.conf.test')

    # override a few things with our test specifics
    django_settings.INSTALLED_APPS = tuple(django_settings.INSTALLED_APPS) + (
        'mailme.tests',
    )


@pytest.fixture(scope='function')
def allow_offline(request, settings):
    try:
        response = requests.get('http://google.com')
    except requests.exceptions.ConnectionError:
        pytest.skip('Test skipped since no internet connection is present.')
