
# # -*- coding: utf-8 -*-
from Products.statusmessages.interfaces import IStatusMessage
from izug.ticketbox import ticketboxMessageFactory as _
from izug.ticketbox.utils import uniquify_ids
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import queryUtility


def generate_datagrid_column_id(obj, event):
    """Generate column-ids for all datagrids in the ticketbox."""

    uniquify_ids(obj.getAvailableStates())
    uniquify_ids(obj.getAvailableReleases())
    uniquify_ids(obj.getAvailablePriorities())
    uniquify_ids(obj.getAvailableAreas())
    uniquify_ids(obj.getAvailableVarieties())


def move_document_to_reference(obj, event):
    """Create own File and add it to References"""

    file_ = obj.getAttachment()
    if file_.data != '':
        new_id = queryUtility(IIDNormalizer).normalize(
            file_.filename.decode('utf-8'))
        if obj.get(new_id, None):
            IStatusMessage(obj.REQUEST).addStatusMessage(
                _(u"text_file_exists_error"), type='error')
            obj.setAttachment('DELETE_FILE')
            return
        new_file_id = obj.invokeFactory(
            type_name="TicketAttachment",
            id=new_id,
            title=file_.filename,
            file=file_)
        new_file = obj.get(new_file_id, None)
        if new_file is None:
            return
        uid = new_file.UID()
        references = obj.getRawAttachments()

        if not isinstance(references, list):
            references = [references]

        references.append(uid)
        obj.setAttachments(references)
        obj.setAttachment('DELETE_FILE')
        obj.reindexObject()
