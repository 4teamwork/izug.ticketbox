"""Definition of the Ticket content type
"""

from zope.interface import implements
from izug.ticketbox import ticketboxMessageFactory as _
from Products.Archetypes.atapi import StringField
from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.Archetypes.atapi import SelectionWidget
# # -*- Message Factory Imported Here -*-

from izug.ticketbox.interfaces import ITicket
from izug.ticketbox.config import PROJECTNAME
from Acquisition import aq_parent

TicketSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    StringField(
        name='State',
        vocabulary_factory='ticketbox_values_states',
        widget=SelectionWidget(
            label=_(u"Select State"),
            description=_(u"Define Which State the Ticket has"),
        ),
        required=True
        ),
    StringField(
        name='Priority',
        vocabulary_factory='ticketbox_values_severities',
        widget=SelectionWidget(
            label=_(u"Select Priority"),
            description=_(u"Select the Priority"),
            ),
            required=False
            ),
    StringField(
        name='Area',
        vocabulary_factory='ticketbox_values_areas',
        widget=SelectionWidget(
            label=_(u'Select Area'),
            description=_(u'Select Area'),
        ),
        required=False
        ),
    StringField(
        name='Releases',
        vocabulary_factory='ticketbox_values_releases',
        widget=SelectionWidget(
            label=_(u'Select Release'),
            description=_(u'Select the Release of the ticket'),
        ),
        required=False
        ),

))


schemata.finalizeATCTSchema(TicketSchema, moveDiscussion=False)


class Ticket(base.ATCTContent):
    """Description of the Example Type"""
    implements(ITicket)

    meta_type = "Ticket"
    schema = TicketSchema

atapi.registerType(Ticket, PROJECTNAME)
