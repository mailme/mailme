
# Folder name mappings, based on http://tools.ietf.org/html/rfc6154
INBOX = 'inbox'
DRAFTS = 'drafts'
SPAM = 'spam'
ARCHIVE = 'archive'
SENT = 'sent'
TRASH = 'trash'
ALL = 'all'
IMPORTANT = 'important'

# Default mapping to unify various provider behaviors
DEFAULT_FOLDER_MAPPING = {
    'inbox': INBOX,
    'drafts': DRAFTS,
    'draft': DRAFTS,
    'junk': SPAM,
    'spam': SPAM,
    'archive': ARCHIVE,
    'sent': SENT,
    'trash': TRASH,
    'all': ALL,
    'important': IMPORTANT,
}
