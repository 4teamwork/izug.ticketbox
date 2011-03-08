"""Definition of the Ticket content type
"""

from zope.interface import implements

from izug.ticketbox import ticketboxMessageFactory as _
from izug.ticketbox.interfaces import ITicket, ITicketBox
from izug.ticketbox.config import PROJECTNAME

from Acquisition import aq_chain
from Acquisition import aq_parent
from transaction import savepoint
from DateTime import DateTime

from Products.Archetypes.atapi import Schema
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import SelectionWidget
from Products.Archetypes.atapi import FileField, FileWidget
from Products.Archetypes.atapi import DateTimeField, CalendarWidget
from Products.Archetypes.atapi import AttributeStorage
from Products.Archetypes.atapi import BooleanField, BooleanWidget
from Products.Archetypes.atapi import ReferenceField
from Products.Archetypes.atapi import registerType
from AccessControl import ClassSecurityInfo
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget


TicketSchema = schemata.ATContentTypeSchema.copy() + Schema((

    #Due-Date (default: x + 14 days)
    DateTimeField(
        name='Due_date',
        default_method='default_due_date',
        widget=CalendarWidget(
            label=_(u"Due-date"),
            description=_(u"Due-date of the ticket"),
        )
    ),

    #State
    StringField(
        name='State',
        vocabulary_factory='ticketbox_values_states',
        widget=SelectionWidget(
            label=_(u"Select State"),
            description=_(u"Define Which State the Ticket has"),
        ),
        required=True
    ),

    #Priority
    StringField(
        name='Priority',
        vocabulary_factory='ticketbox_values_severities',
        widget=SelectionWidget(
            label=_(u"Select Priority"),
            description=_(u"Select the Priority"),
        ),
    ),

    #Area
    StringField(
        name='Area',
        vocabulary_factory='ticketbox_values_areas',
        widget=SelectionWidget(
            label=_(u'Select Area'),
            description=_(u'Select Area'),
        ),
    ),

    #Releases
    StringField(
        name='Releases',
        vocabulary_factory='ticketbox_values_releases',
        widget=SelectionWidget(
            label=_(u'Select Release'),
            description=_(u'Select the Release of the ticket'),
        ),
    ),

    #Responsible
    StringField(
        name='responsibleManager',
        index="FieldIndex:schema",
        widget=SelectionWidget(
            label="Responsible",
            description="Select which manager, if any," +
                " is responsible for this issue.",
        ),
        required=True,
        vocabulary='get_assignable_users',
    ),
    #Answer-date (default: x + 14 days)
    DateTimeField(
        name='Answer_date',
        default_method='default_answer_date',
        widget=CalendarWidget(
            label=_(u"Answer-date"),
            description=_(u"Answer-date of the ticket"),
        )
    ),

    #Attachment
    FileField(
        name='Attachment',
        widget=FileWidget(
            label=_(u"Attachment"),
            description=_(u"You may optionally upload a file attachment." +
                " Please do not upload unnecessarily large files."),
        ),
        storage=AttributeStorage(),
    ),

    #References
    ReferenceField(
        name='references',
        widget=ReferenceBrowserWidget(
            label=_(u"References"),
            allow_browse=True,
            show_results_without_query=True,
            restrict_browsing_to_startup_directory=True,
            base_query={"portal_type": "Ticket Box", "sort_on": "sortable_title"},
        ),
        allowed_types=('Ticket','Ticket Box'),
        multiValued=1,
        schemata='default',
        relationship='Ticket Box'
    ),

    #send Notification Emails
    BooleanField(
        name='sendNotificationEmails',
        default=True,
        widget=BooleanWidget(
            label=_(u"Send notification emails"),
            description=_(u"If selected, tracker managers will receive an email" +
                " each time a new issue or response is posted, and issue" +
                " submitters will receive an email when there is a new" +
                " response and when an issue has been resolved," +
                " awaiting confirmation."),
        )
    ),
))

schemata.finalizeATCTSchema(TicketSchema, moveDiscussion=False)

class Ticket(base.ATCTContent):
    """Description of the Example Type"""
    implements(ITicket)

    security = ClassSecurityInfo()
    meta_type = "Ticket"
    schema = TicketSchema

    security.declarePrivate('linkDetection')
    def _renameAfterCreation(self, check_auto_id=False):
        """rename id and title after creation

        save a unique id and the title with the id nr.
        """
        parent = self.get_tracker()
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

    def get_tracker(self):
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

    def default_due_date(self):
        """ Return a standard due-date (9.00 Clock in 14 days) """

        a = DateTime() + 14
        return DateTime(a.year(), a.month(), a.day(), 9, 00)

    def default_answer_date(self):
        """ Return a standard answer-date (9.00 Clock in 14 days) """

        return self.default_due_date()

    def send_notification_mail(self):
        """ Send a notification from the ticket
        """

        #TODO: implement notification
        print "send email"

    def get_assignable_users(self):
        """
        Get the managers available as a DisplayList. The first item is 'None',
        with a key of '(UNASSIGNED)'.
        """

        return aq_parent(self).get_assignable_users()


registerType(Ticket, PROJECTNAME)
