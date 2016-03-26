import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mailme.settings')

from django.conf import settings

from celery import Celery

celery = Celery('mailme')

celery.config_from_object('django.conf:settings')
celery.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
