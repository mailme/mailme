import imapclient

# Special folders, see RFC6154 - http://tools.ietf.org/html/rfc6154
INBOX = 'inbox'
DRAFTS = 'drafts'
JUNK = 'spam'
ARCHIVE = 'archive'
SENT = 'sent'
TRASH = 'trash'
ALL = 'all'
IMPORTANT = 'important'

# Personal namespaces that are common among providers
# used as a fallback when the server does not support the NAMESPACE capability
_POPULAR_PERSONAL_NAMESPACES = ((', '), ('INBOX.', '.'))

# Names of special folders that are common among providers
POPULAR_SPECIAL_FOLDERS = {
    SENT: ('Sent', 'Sent Items', 'Sent items', 'Sent Messages'),
    DRAFTS: ('Drafts',),
    ARCHIVE: ('Archive',),
    TRASH: ('Trash', 'Deleted Items', 'Deleted Messages'),
    JUNK: ('Junk', 'Spam', 'Junk Mail', 'Bulk Mail')
}

REVERSE_POPULAR_SPECIAL_FOLDERS = {}

for key, folder_list in POPULAR_SPECIAL_FOLDERS.items():
    for folder in folder_list:
        REVERSE_POPULAR_SPECIAL_FOLDERS[folder] = key

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
    'junk': JUNK,
    'spam': JUNK,
    'archive': ARCHIVE,
    'sent': SENT,
    'sent items': SENT,
    'trash': TRASH,
    'all': ALL,
    'important': IMPORTANT,
}

DEFAULT_FOLDER_FLAGS = {
    br'\All': ALL,
    br'\Archive': ARCHIVE,
    br'\Drafts': DRAFTS,
    br'\Inbox': INBOX,
    br'\Junk': JUNK,
    br'\Sent': SENT,
    br'\Spam': JUNK,
    br'\Trash': TRASH,
}
