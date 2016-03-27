# -*- coding: utf-8 -*-
from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property

from mailme.utils.avatar import get_profile_image
from mailme.utils.db import MailmeModel
from mailme.utils.uri import parse_uri

from .transports.imap import ImapTransport


class User(MailmeModel, AbstractBaseUser):
    username = models.CharField(_('Username'), unique=True, max_length=256)
    name = models.TextField(_('Name'), max_length=100, blank=True, null=True)
    is_active = models.BooleanField(
        _('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    # Required for django-admin
    is_staff = models.BooleanField(
        _('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_superuser = models.BooleanField(
        _('superuser status'), default=False,
        help_text=_('Designates that this user has all permissions without '
                    'explicitly assigning them.'))

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return self.username

    def has_module_perms(self, app_label):
        return self.is_superuser

    def has_perm(self, app_label):
        return self.is_superuser

    def get_absolute_url(self):
        return ''

    def get_display_name(self):
        return self.username

    def get_short_name(self):
        return self.get_display_name()

    @property
    def profile_image(self):
        return get_profile_image(self)


ALLOWED_MIMETYPES = {'text/plain', 'text/html'}


class Mailbox(models.Model):
    name = models.CharField(
        _(u'Name'),
        max_length=256,
    )

    uri = models.CharField(
        _(u'URI'),
        max_length=256,
        help_text=(_(
            'Example: imap+ssl://myusername:mypassword@someserver'
        )),
        blank=True,
        null=True,
        default=None,
    )

    from_email = models.CharField(
        _(u'From email'),
        max_length=255,
        blank=True,
        null=True,
        default=None,
    )

    active = models.BooleanField(
        _(u'Active'),
        blank=True,
        default=True,
    )

    objects = models.Manager()

    @cached_property
    def parsed_uri(self):
        return parse_uri(self.uri)

    def get_connection(self):
        """Returns the transport instance for this mailbox."""
        if not self.uri:
            return None

        uri = self.parsed_uri

        if uri.scheme == 'imap':
            conn = ImapTransport(
                uri.location,
                port=uri.port if uri.port else None,
                ssl=uri.use_ssl,
            )
            conn.connect(uri.username, uri.password)
        return conn

    def get_new_mail(self, condition=None, folder=None):
        """Connect to this transport and fetch new messages."""
        new_mail = []
        connection = self.get_connection()
        if not connection:
            return new_mail

        messages = connection.get_messages(condition=condition, folder=folder)

        for message in messages:
            new_mail.append(Message(subject=message))

        return new_mail

    def __str__(self):
        return self.name


class Message(models.Model):
    mailbox = models.ForeignKey(Mailbox, related_name='messages')
    subject = models.CharField(
        _(u'Subject'),
        max_length=255
    )

    def __str__(self):
        return self.subject

    def __repr__(self):
        return '<Message({})>'.format(self.subject)
