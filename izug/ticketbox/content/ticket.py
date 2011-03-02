"""Definition of the Ticket content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-

from izug.ticketbox.interfaces import ITicket
from izug.ticketbox.config import PROJECTNAME

TicketSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

))


schemata.finalizeATCTSchema(TicketSchema, moveDiscussion=False)


class Ticket(base.ATCTContent):
    """Description of the Example Type"""
    implements(ITicket)

    meta_type = "Ticket"
    schema = TicketSchema


atapi.registerType(Ticket, PROJECTNAME)
