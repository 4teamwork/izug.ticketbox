from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from ftw.workspace.interfaces import IWorkspace
from ftw.workspace.interfaces import IWorkspaceLayer
from izug.ticketbox.interfaces import ITicket
from izug.ticketbox.interfaces import ITicketReferenceStartupDirectory
from zope.component import adapts
from zope.interface import implements


class WorkspaceStartupDirectory(object):
    implements(ITicketReferenceStartupDirectory)
    adapts(ITicket, IWorkspaceLayer)

    def __init__(self, ticket, request):
        self.ticket = ticket
        self.request = request

    def get(self):
        url_tool = self.ticket.restrictedTraverse('@@plone_tools').url()
        startup_obj = self.get_workspace() or self.ticket
        return '/'.join(url_tool.getRelativeContentPath(startup_obj))

    def get_workspace(self):
        context = self.ticket
        while context and not IPloneSiteRoot.providedBy(context):
            if IWorkspace.providedBy(context):
                return context
            context = aq_parent(aq_inner(context))
