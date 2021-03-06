import os

import environ
from kombu import Queue

env = environ.Env()

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_DIR = os.path.join(BASE_DIR, '..', '..')

SECRET_KEY = 'na2p&yexkp-g83$2m^&b!r+a%nv2ci1!d9vh^a_7h!hv*7&h79'

SITE_ID = 1

DEBUG = True

INSTALLED_APPS = (
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',

    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Asyncronous worker support
    'celery',

    # i18n/l10n
    'django_babel',

    # For our REST Api
    'rest_framework',

    # mailme apps
    'mailme',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'mailme.urls'

WSGI_APPLICATION = 'mailme.wsgi.application'

AUTH_USER_MODEL = 'mailme.User'

DATABASES = {
    'default': env.db_url(default='psql://postgres:@localhost/mailme')
}

# Run all views in a transaction unless they are decorated not to.
DATABASES['default']['ATOMIC_REQUESTS'] = True

# Pool our database connections up for 300 seconds
DATABASES['default']['CONN_MAX_AGE'] = 300


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_DIR, 'src', 'mailme', 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.core.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

STATICFILES_DIRS = (
    os.path.join(PROJECT_DIR, 'src', 'mailme', 'static'),
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 10,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(PROJECT_DIR, 'web', 'static')

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'web', 'media')

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


## Celery
BROKER_URL = 'redis://localhost:6379'

CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_BROKER_CONNECTION_TIMEOUT = 0.1
CELERY_BROKER_HEARTBEAT = 60 * 15
CELERY_TASK_DEFAULT_QUEUE = 'default'
CELERY_RESULT_BACKEND = env(
    'CELERY_RESULT_BACKEND', default='redis://localhost:6379/1')

CELERY_TASK_IGNORE_RESULT = True
CELERY_SEND_TASK_ERROR_EMAILS = True
CELERY_WORKER_HIJACK_ROOT_LOGGER = False

# Just so that this won't be forgotten, see
# http://docs.celeryproject.org/en/latest/getting-started/brokers/redis.html#caveats
# for details.
BROKER_TRANSPORT_OPTIONS = {
    'fanout_prefix': True,
    'fanout_patterns': True
}

# Force always eager to be False (it's by default but here for documentation)
CELERY_ALWAYS_EAGER = False
CELERY_EAGER_PROPAGATES_EXCEPTIONS = False

# Only accept JSON. This will be the default in Celery 3.2
CELERY_ACCEPT_CONTENT = ['json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'

# Track started tasks. This adds a new STARTED state once a task
# is started by the celery worker.
CELERY_TRACK_STARTED = True

CELERY_IMPORTS = (
    'mailme.tasks.mail',
)

CELERY_QUEUES = (
    Queue('default', routing_key='default'),
    Queue('celery', routing_key='celery'),
)

# Make our `LOGGING` configuration the only truth and don't let celery
# overwrite it.
CELERYD_HIJACK_ROOT_LOGGER = False

# Don't log celery log-redirection as warning (default).
# We manage our logging through `django.conf.settings.LOGGING` and
# want that to be our first-citizen config.
CELERY_REDIRECT_STDOUTS_LEVEL = 'INFO'

# Django security related settings.
SECURE_SSL_REDIRECT = True

# Commit to HTTPS only for 12 months (HSTS)
# SECURE_HSTS_SECONDS = 31536000

# prevent framing
SECURE_FRAME_DENY = True

# Don't let the browser guess content-types
SECURE_CONTENT_TYPE_NOSNIFF = True

# Enable browser XSS Filter
SECURE_BROWSER_XSS_FILTER = True

# Force cookies to be https only (or at least tell the browsers to do so...)
SESSION_COOKIE_SECURE = True

SESSION_COOKIE_HTTPONLY = True

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]

# Django REST Framework related settings.
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'mailme.api.auth.JSONWebTokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'mailme.api.parsers.JSONParser',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'mailme.api.renderers.JSONRenderer',
    ),
}
