from plone.indexer.decorator import indexer
from izug.ticketbox.interfaces import ITicket
from Products.CMFPlone.utils import safe_unicode
from Products.CMFPlone.utils import safe_callable
import re

num_sort_regex = re.compile('\d+')

@indexer(ITicket)
def sortable_id(obj):
    _id = getattr(obj, 'getId', None)
    if _id is not None:
        if safe_callable(_id):
            _id = _id()
        if isinstance(_id, basestring):
            sortable_id = _id.lower().strip()
            # Replace numbers with zero filled numbers
            sortable_id = num_sort_regex.sub(zero_fill, sortable_id)
            # Truncate to prevent bloat
            sortable_id = safe_unicode(sortable_id)[:40].encode('utf-8')
            return sortable_id
    return ''

def zero_fill(matchobj):
    return matchobj.group().zfill(8)
