from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner
from Acquisition import aq_parent
from plone import api
from izug.ticketbox.config import PROJECTNAME
from izug.ticketbox.content.ticket import Ticket
from izug.ticketbox.interfaces import ISubTicket
from Products.Archetypes.atapi import registerType
from Products.ATContentTypes.content import schemata
from zope.interface import implements


subticket_schema = Ticket.schema.copy()
del subticket_schema['classification']
subticket_schema['title'].default_method = 'default_title'
subticket_schema['description'].default_method = 'default_description'
schemata.finalizeATCTSchema(subticket_schema, moveDiscussion=False)


class SubTicket(Ticket):
    implements(ISubTicket)

    security = ClassSecurityInfo()
    meta_type = "SubTicket"
    schema = subticket_schema

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

    def default_title(self):
        ticket = self.get_referring_ticket()
        return ticket.Title() if ticket else ''

    def default_description(self):
        ticket = self.get_referring_ticket()
        return ticket.getRawDescription() if ticket else ''

    def get_referring_ticket(self):
        ticket = None
        ticket_uuid = self.REQUEST.get('ticket', None)
        if ticket_uuid:
            ticket = api.content.get(UID=ticket_uuid)
        return ticket

registerType(SubTicket, PROJECTNAME)
