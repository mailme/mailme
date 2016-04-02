# -*- coding: utf-8 -*-
import pytz

from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property

from mailme.providers import provider_from_address
from mailme.utils.avatar import get_profile_image
from mailme.utils.db import MailmeModel
from mailme.utils.uri import parse_uri


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


class MailboxFolder(models.Model):
    """Represents a folder in a mailbox.

    This is used purely for syncing purposes, we do store folders
    as flags on messages but don't represent a regular imap mailbox.
    """
    mailbox = models.ForeignKey('Mailbox', related_name='folders')
    name = models.CharField(_('Folder name'), max_length=256)

    # Imap sync related
    uidvalidity = models.BigIntegerField()
    highestmodseq = models.BigIntegerField(null=True, blank=True)
    uidnext = models.PositiveIntegerField(null=True, blank=True)


class Mailbox(models.Model):
    name = models.CharField(_(u'Name'), max_length=256)
    user = models.ForeignKey(User)

    uri = models.CharField(
        _(u'URI'), max_length=256,
        help_text=(_('Example: imap+ssl://myusername:mypassword@someserver')),
        blank=True, null=True, default=None)

    provider = models.CharField(
        _('Provider'), max_length=256, null=True, blank=True)

    from_email = models.CharField(
        _(u'From email'), max_length=255,
        blank=True, null=True, default=None)

    active = models.BooleanField(_(u'Active'), blank=True, default=True)

    objects = models.Manager()

    @cached_property
    def parsed_uri(self):
        return parse_uri(self.uri)

    def get_provider(self, email):
        try:
            return provider_from_address(email)
        except KeyError:
            return None

    def get_connection(self):
        """Returns the transport instance for this mailbox."""
        if not self.uri:
            return None

        # Circular imports
        from .transports.imap import ImapTransport

        uri = self.parsed_uri

        if uri.scheme == 'imap':
            conn = ImapTransport(
                uri.location,
                ssl=uri.use_ssl,
                provider=self.provider
            )
            conn.connect(uri.username, uri.password)
        return conn

    def sync(self, condition=None, folder=None):
        """Connect to this transport and fetch new messages."""
        new_mail = []
        connection = self.get_connection()
        if not connection:
            return new_mail

        messages = connection.get_messages(condition=condition, folder=folder)

        # TODO:
        # * handle attachments
        # * normalize html

        for message in messages:
            date = message['parsed_date']

            if timezone.is_naive(date):
                # If no timezone is given, UTC should be used
                date = timezone.make_aware(date, pytz.UTC)

            new_mail.append(Message(
                message_id=message['message_id'],
                original=message['original'],
                date=date,
                subject=message['subject'],
                plain_body=message['body']['plain'],
                html_body=message['body']['html'],
                sent_from=message['from'],
                to=message['to'],
                bcc=message['bcc'],
                cc=message['cc'],
                headers=message['headers'],
            ))

        Message.objects.bulk_create(new_mail)

        return new_mail

    def __str__(self):
        return self.name


class Thread(models.Model):
    mailbox = models.ForeignKey(Mailbox, related_name='threads')
    subject = models.CharField(max_length=256)

    # TODO:
    # * read (boolean, wether there are messages in the thread that are unread)
    # * starred (flagged)
    # * folders


class Message(models.Model):
    thread = models.ForeignKey(Thread, related_name='messages')
    folder = models.ForeignKey(MailboxFolder, related_name='messages')

    from_address = JSONField(_('Sent from'), blank=True, default=[])
    to_address = JSONField(_('Sent to'), blank=True, default=[])
    cc_address = JSONField(_('CC'), blank=True, default=[])
    bcc_address = JSONField(_('BCC'), blank=True, default=[])
    reply_to = JSONField(_('Reply-To'), blank=True, null=True)
    in_reply_to = JSONField(_('In reply to'), blank=True, null=True)

    headers = JSONField(_('Headers'), blank=True, default={})
    subject = models.CharField(_('Subject'), max_length=255)
    original = models.TextField(_('Original (raw) text'))
    plain_body = models.TextField(_('Text'), blank=True)
    html_body = models.TextField(_('HTML'), blank=True)
    date = models.DateTimeField(_('Date'), blank=True)

    # From: http://tools.ietf.org/html/rfc4130, section 5.3.3,
    # max message_id_header is 998 characters
    message_id = models.CharField(max_length=998)
    references = JSONField(_('References'), blank=True, null=True)

    # Imap sync related metadata
    uid = models.BigIntegerField(db_index=True)

    # TODO:
    # * attachments
    # * read
    # * starred (flagged)

    def __str__(self):
        return self.subject

    def __repr__(self):
        return '<Message({})>'.format(self.subject)
