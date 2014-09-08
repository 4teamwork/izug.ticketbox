from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner
from Acquisition import aq_parent
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
        parent = aq_parent(aq_inner(self))
        existing = parent.objectIds()
        prefix = parent.getId()

        counter = 0
        while True:
            counter += 1
            new_id = '.'.join((prefix, str(counter)))
            if new_id not in existing:
                return new_id

registerType(SubTicket, PROJECTNAME)
