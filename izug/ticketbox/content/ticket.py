"""Definition of the Ticket content type
"""

from zope.interface import implements
from izug.ticketbox import ticketboxMessageFactory as _
from Products.Archetypes.atapi import StringField
from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.Archetypes.atapi import SelectionWidget
from Products.Archetypes.atapi import FileField
from Products.Archetypes.atapi import FileWidget
from Products.Archetypes.atapi import AttributeStorage
# # -*- Message Factory Imported Here -*-

from izug.ticketbox.interfaces import ITicket, ITicketBox
from izug.ticketbox.config import PROJECTNAME
from Acquisition import aq_chain
from transaction import savepoint

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

    FileField(
        name='attachment',
        widget=FileWidget(
            label=_(u"Attachment"),
            description=_(u"You may optionally upload a file attachment. Please do not upload unnecessarily large files."),
        ),
        storage=AttributeStorage(),
    ),

))

schemata.finalizeATCTSchema(TicketSchema, moveDiscussion=False)

class Ticket(base.ATCTContent):
    """Description of the Example Type"""
    implements(ITicket)

    meta_type = "Ticket"
    schema = TicketSchema

    def _renameAfterCreation(self, check_auto_id=False):
        """rename id and title after creation

        save a unique id and the title with the id nr.
        """
        parent = self.getTracker()
        maxId = 0
        for id in parent.objectIds():
            try:
                intId = int(id)
                maxId = max(maxId, intId)
            except (TypeError, ValueError):
                pass
        newId = str(maxId + 1)
        # Can't rename without a subtransaction commit when using
        # portal_factory!
        savepoint(optimistic=True)
        self.setId(newId)
        self.setTitle("#%s - %s" % (newId, self.title))

        self.reindexObject(idxs=['Title'])
        self.reindexObject(idxs=['Id'])

    def getTracker(self):
        """Return the tracker.

        This gets around the problem that the aq_parent of an issue
        that is being created is not the tracker, but a temporary
        folder.
        """
        for parent in aq_chain(self):
            if ITicketBox.providedBy(parent):
                return parent
        raise Exception(
            "Could not find TicketBox in acquisition chain of %r" %
            self)



atapi.registerType(Ticket, PROJECTNAME)
