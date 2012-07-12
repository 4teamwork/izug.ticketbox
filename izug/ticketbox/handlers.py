
# # -*- coding: utf-8 -*-
from izug.ticketbox import ticketboxMessageFactory as _
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import queryUtility


def generate_datagrid_column_id(obj, event):
    """Generate column-ids for all datagrids in the ticketbox."""

    datagrid = []

    #save datagrid to change ids
    datagrid.append(obj.getAvailableStates())
    datagrid.append(obj.getAvailableReleases())
    datagrid.append(obj.getAvailablePriorities())
    datagrid.append(obj.getAvailableAreas())
    datagrid.append(obj.getAvailableVarieties())

    #change id from datagrids
    for dg in datagrid:
        for row in dg:
            if not row['id']:
                name = row['title']
                row['id'] = queryUtility(IIDNormalizer).normalize(
                    name.decode('utf-8'))


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
