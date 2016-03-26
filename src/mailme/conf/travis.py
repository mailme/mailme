import os

from mailme.conf.test import *


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ['MAILME_TEST_DB_NAME'],
        'USER': os.environ['MAILME_TEST_DB_USER']
    }
}

os.environ['ON_TRAVIS'] = 'true'
