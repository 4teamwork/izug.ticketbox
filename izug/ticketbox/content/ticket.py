from AccessControl import ClassSecurityInfo
from Acquisition import aq_parent
from DateTime import DateTime
from izug.ticketbox import ticketboxMessageFactory as _
from izug.ticketbox.config import PROJECTNAME
from izug.ticketbox.interfaces import ITicket
from plone.i18n.normalizer import IDNormalizer
from Products.Archetypes.atapi import AttributeStorage
from Products.Archetypes.atapi import DateTimeField, CalendarWidget
from Products.Archetypes.atapi import FileField, FileWidget
from Products.Archetypes.atapi import ReferenceField
from Products.Archetypes.atapi import registerType
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import SelectionWidget
from Products.Archetypes.atapi import StringField
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget \
    import ReferenceBrowserWidget
from Products.statusmessages.interfaces import IStatusMessage
from zope.interface import implements

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
            format="select",
            label=_(u"Select State"),
            description=_(u"Define Which State the Ticket has"),
        ),
    ),

    #Priority
    StringField(
        name='Priority',
        vocabulary_factory='ticketbox_values_priorities',
        widget=SelectionWidget(
            format="select",
            label=_(u"Select Priority"),
            description=_(u"Select the Priority"),
        ),
    ),

    #Area
    StringField(
        name='Area',
        vocabulary_factory='ticketbox_values_areas',
        widget=SelectionWidget(
            format="select",
            label=_(u'Select Area'),
            description=_(u'Select Area'),
        ),
    ),

    #Releases
    # XXX: RENAME TO RELEASE
    StringField(
        name='Releases',
        vocabulary_factory='ticketbox_values_releases',
        widget=SelectionWidget(
            format="select",
            label=_(u'Select Release'),
            description=_(u'Select the Release of the ticket'),
        ),
    ),

    #Responsible
    StringField(
        name='responsibleManager',
        index="FieldIndex:schema",
        widget=SelectionWidget(
            format="select",
            label="Responsible",
            description="Select which manager, if any," +
                " is responsible for this issue.",
        ),
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

    #References for Atachments
    ReferenceField(
        name='attachments',
        widget=ReferenceBrowserWidget(
            label=_(u"Attachments"),
            allow_browse=True,
            show_results_without_query=True,
            restrict_browsing_to_startup_directory=True,
            base_query={
                "portal_type": "TicketAttachment",
                "sort_on": "sortable_title"},
            visible={'view': 'visible', 'edit': 'invisible'},
        ),
        allowed_types=('TicketAttachment'),
        multiValued=1,
        schemata='default',
        relationship='TicketAttachment'
    ),

    #References
    ReferenceField(
        name='ticketReferences',
        widget=ReferenceBrowserWidget(
            label=_(u"References"),
            allow_browse=True,
            show_results_without_query=True,
            restrict_browsing_to_startup_directory=True,
            base_query={"portal_type": "Ticket Box",
                        "sort_on": "sortable_title"},
        ),
        allowed_types=('Ticket', 'Ticket Box', 'TicketAttachment'),
        multiValued=1,
        schemata='default',
        relationship='TicketBox'
    ),
))

TicketSchema['description'].required = True
schemata.finalizeATCTSchema(TicketSchema, moveDiscussion=False)


class Ticket(base.ATCTFolder):
    """A ticket for a tracker-like task management system"""
    implements(ITicket)

    security = ClassSecurityInfo()
    meta_type = "Ticket"
    schema = TicketSchema

    def generateNewId(self):
        """generate a new ticket id.
        get all tickets from parent (ticketbox)
        and looks for the higherst id and add one to be unique
        """
        parent = self.aq_parent
        maxId = 0
        for id in parent.objectIds():
            try:
                intId = int(id)
                maxId = max(maxId, intId)
            except (TypeError, ValueError):
                pass
        return str(maxId + 1)

    def default_due_date(self):
        """ Return a standard due-date (9.00 Clock in 14 days) """

        a = DateTime() + 14
        return DateTime(a.year(), a.month(), a.day(), 9, 00)

    def default_answer_date(self):
        """ Return a standard answer-date (9.00 Clock in 14 days) """

        return self.default_due_date()

    def get_assignable_users(self):
        """
        Get the managers available as a DisplayList. The first item is 'None',
        with a key of '(UNASSIGNED)'.
        """

        return aq_parent(self).get_assignable_users()


registerType(Ticket, PROJECTNAME)


def move_document_to_reference(obj, event):
    """Create own File and add it to References"""
    file_ = obj.getAttachment()
    if file_.data != '':
        new_id = IDNormalizer.normalize(IDNormalizer(), file_.filename)

        if obj.get(new_id, None):
            IStatusMessage(obj.REQUEST).addStatusMessage(
                _(u"A File with this id already exists,\
                the File wasn't uploaded"), type='error')
            obj.setAttachment('DELETE_FILE')
            return
        new_file_id = obj.invokeFactory(
            type_name="TicketAttachment",
            id=new_id,
            title=file_.filename,
            file=file_)
        new_file = obj.get(new_file_id, None)
        if new_file is None:
            return
        uid = new_file.UID()
        import pdb; pdb.set_trace( )
        references = obj.getRawAttachments()

        if not isinstance(references, list):
            references = [references]

        references.append(uid)
        obj.setAttachments(references)
        obj.setAttachment('DELETE_FILE')
        obj.reindexObject()
