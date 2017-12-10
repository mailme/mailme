import imapclient

# Folder name mappings, based on http://tools.ietf.org/html/rfc6154
INBOX = 'inbox'
DRAFTS = 'drafts'
SPAM = 'spam'
ARCHIVE = 'archive'
SENT = 'sent'
TRASH = 'trash'
ALL = 'all'
IMPORTANT = 'important'

# System flags
DELETED = imapclient.DELETED
SEEN = imapclient.SEEN
ANSWERED = imapclient.ANSWERED
FLAGGED = imapclient.FLAGGED
DRAFT = imapclient.DRAFT
RECENT = imapclient.RECENT

IGNORE_FOLDER_NAMES = (
    '\\Noselect', '\\NoSelect', '\\NonExistent'
)

# Default mapping to unify various provider behaviors
DEFAULT_FOLDER_MAPPING = {
    'inbox': INBOX,
    'drafts': DRAFTS,
    'draft': DRAFTS,
    'junk': SPAM,
    'spam': SPAM,
    'archive': ARCHIVE,
    'sent': SENT,
    'sent items': SENT,
    'trash': TRASH,
    'all': ALL,
    'important': IMPORTANT,
}

DEFAULT_FOLDER_FLAGS = {
    '\\Trash': 'trash',
    '\\Sent': 'sent',
    '\\Drafts': 'drafts',
    '\\Junk': 'spam',
    '\\Inbox': 'inbox',
    '\\Spam': 'spam'
}
