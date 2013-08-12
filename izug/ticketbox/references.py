from izug.ticketbox.interfaces import ITicket
from izug.ticketbox.interfaces import ITicketReferenceStartupDirectory
from zope.component import adapts
from zope.interface import Interface
from zope.interface import implements


class DefaultTicketReferenceStartupDirectory(object):
    implements(ITicketReferenceStartupDirectory)
    adapts(ITicket, Interface)

    def __init__(self, ticket, request):
        self.ticket = ticket
        self.request = request

    def get(self):
        url_tool = self.ticket.restrictedTraverse('@@plone_tools').url()
        path = '/'.join(url_tool.getRelativeContentPath(self.ticket))
        return path
