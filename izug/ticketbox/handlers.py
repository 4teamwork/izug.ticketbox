
# # -*- coding: utf-8 -*-
from Products.statusmessages.interfaces import IStatusMessage
from izug.ticketbox import ticketboxMessageFactory as _
from izug.ticketbox.utils import uniquify_ids
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import queryUtility
from Products.CMFCore.utils import getToolByName
from DateTime import DateTime


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
            type_name="File",
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


def set_workflow_state(obj, event):
    if not obj.getField('classification'):
        return

    mtool = getToolByName(obj, 'portal_membership')
    current_user = mtool.getAuthenticatedMember().getId()
    wftool = getToolByName(obj, 'portal_workflow')
    wf_ids = wftool.getChainFor(obj)
    state = obj.getClassification()
    wf_id = wf_ids[0]
    comment = 'State set to: %s' % state
    wftool.setStatusOf(wf_id, obj, {'review_state': state,
                                    'action': state,
                                    'actor': current_user,
                                    'time': DateTime(),
                                    'comments': comment, })
    wftool = wftool.getWorkflowById(wf_id)
    wftool.updateRoleMappingsFor(obj)
    obj.reindexObjectSecurity()


def authorize_assigned_user(obj, event):
    assigned_user = obj.getResponsibleManager()
    current_roles = dict(obj.get_local_roles()).get(assigned_user, ())
    new_roles = list(set(list(current_roles) + ['Editor']))
    obj.manage_setLocalRoles(assigned_user, new_roles)
    obj.reindexObjectSecurity()
