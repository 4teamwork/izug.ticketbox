"""Definition of the Ticket content type
"""

from zope.interface import implements
from izug.ticketbox import ticketboxMessageFactory as _
from Products.Archetypes.atapi import StringField, StringWidget
from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.Archetypes.atapi import TextField, TextAreaWidget
from Products.Archetypes.atapi import SelectionWidget
# # -*- Message Factory Imported Here -*-

from izug.ticketbox.interfaces import ITicket
from izug.ticketbox.config import PROJECTNAME

TicketSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-
    StringField(
         name='title',
         widget=StringWidget(
             label=_(u"Ticketbox name"),
             description=(u"Enter a descriptive name for this Ticketbox"),
         ),
         required=True,
         searchable=True
    ),
    #Description
    TextField(
        name='description',
        widget=TextAreaWidget(
            label=_(u"Ticketbox description"),
            description=_(u"Describe the purpose of this Ticketbox"),
        ),
        required=True,
        searchable=True
    ),
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
