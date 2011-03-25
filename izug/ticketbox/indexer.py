from izug.ticketbox.interfaces import ITicket
from plone.indexer.decorator import indexer
from Products.CMFPlone.utils import safe_callable
from Products.CMFPlone.utils import safe_unicode
from izug.ticketbox.browser.helper import readable_author
from Products.ATContentTypes.interface.file import IATFile
import re

num_sort_regex = re.compile('\d+')


@indexer(ITicket)
def sortable_id(obj):
    """put any zeros before the id
    so its possible to sort the id correctly
    """

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


@indexer(IATFile)
def sortable_ticket_references(obj):
    """put any zeros before the id
    so its possible to sort the id correctly
    """

    parent = obj.aq_inner.aq_parent
    if ITicket.providedBy(parent):
        return sortable_id(obj)


def zero_fill(matchobj):
    return matchobj.group().zfill(8)


@indexer(ITicket)
def sortable_responsibleManager(obj):
    """get the fullname of the author to sort correctly"""
    author = readable_author(obj)
    if isinstance(author, unicode):
        author = author.encode('utf-8')
    return author