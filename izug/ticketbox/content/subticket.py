from AccessControl import ClassSecurityInfo
from izug.ticketbox.config import PROJECTNAME
from izug.ticketbox.content.ticket import Ticket
from izug.ticketbox.interfaces import ISubTicket
from Products.Archetypes.atapi import registerType
from zope.interface import implements


schema = Ticket.schema.copy()


class SubTicket(Ticket):
    implements(ISubTicket)

    security = ClassSecurityInfo()
    meta_type = "SubTicket"
    schema = schema

    def generateNewId(self):
        """generate a new ticket id.
        get all tickets from parent (ticketbox)
        and looks for the higherst id and add one to be unique
        """
        parent = self.aq_parent
        maxId = 0
        for id_ in parent.objectIds():
            try:
                intId = int(id_)
                maxId = max(maxId, intId)
            except (TypeError, ValueError):
                pass
        return '.'.join((parent.getId(), str(maxId + 1)))

registerType(SubTicket, PROJECTNAME)
