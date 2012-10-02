from AccessControl import ClassSecurityInfo
from Acquisition import aq_parent
from DateTime import DateTime
from izug.ticketbox import ticketboxMessageFactory as _
from izug.ticketbox.config import PROJECTNAME
from izug.ticketbox.interfaces import ITicket
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
from zope.interface import implements
from Products.Archetypes import atapi
from Products.CMFCore.permissions import ManagePortal

TicketSchema = schemata.ATContentTypeSchema.copy() + Schema((

        #Due-Date (default: x + 14 days)
        DateTimeField(
            name='dueDate',
            default_method='default_due_date',
            required=True,
            validators=('isValidDate'),
            widget=CalendarWidget(
                label=_(u"label_duedate", default=u"Due Date"),
                description=_(u"help_duedate",
                              default=u"Due-date of the ticket"))),

        #State
        StringField(
            name='state',
            vocabulary_factory='ticketbox_values_states',
            widget=SelectionWidget(
                format="select",
                label=_(u"label_state", default=u"State"),
                description=_(u"help_state",
                              default=u"Define Which State the Ticket has"))),

        #Priority
        StringField(
            name='priority',
            vocabulary_factory='ticketbox_values_priorities',
            widget=SelectionWidget(
                format="select",
                label=_(u"label_select_priority",
                        default=u"Select Priority"),
                description=_(u"help_priority",
                              default=u"Select the Priority"))),

        #Area
        StringField(
            name='area',
            vocabulary_factory='ticketbox_values_areas',
            widget=SelectionWidget(
                format="select",
                label=_(u"label_select_area", default=u'Select Area'),
                description=_(u'help_area',
                              default=u'Select the Area of the ticket'))),

        #Variety
        StringField(name='variety',
                    vocabulary_factory='ticketbox_values_varieties',

                    widget=SelectionWidget(
                label=_(u"label_select_variety",
                        default=u'Select Variety'),
                description=_(
                    u'help_variety',
                    default=u'Select the Variety of the ticket'),
                format="select")),

        #Releases
        # XXX: RENAME TO RELEASE
        StringField(
            name='releases',
            vocabulary_factory='ticketbox_values_releases',
            widget=SelectionWidget(
                format="select",
                label=_(u'label_select_release', default=u'Select Release'),
                description=_(u'help_release',
                              default=u'Select the Release of the ticket'))),

        #Watched in release
        StringField(
            name='watchedRelease',
            vocabulary_factory='ticketbox_values_releases',
            widget=SelectionWidget(
                format="select",
                label=_(u'label_select_watchedRelease',
                        default=u'Select watched in release'),
                description=_(
                    u'help_watchedRelease',
                    default=u'Select in which release you watched it'))),

        #Responsible
        StringField(
            name='responsibleManager',
            index="FieldIndex:schema",
            vocabulary='assignable_users',
            widget=SelectionWidget(
                format="select",
                label=_(u'label_Responsible',
                        default=u"Responsible"),
                description=_(u'help_responsible',
                              default=u"Select which manager, if any," +
                              " is responsible for this issue."))),

        #Answer-date (default: x + 14 days)
        DateTimeField(
            name='answerDate',
            default_method='default_answer_date',
            widget=CalendarWidget(
                label=_(u'label_AnswerDate',
                        default=u"Answer Date"),
                description=_(u'help_answerdated',
                              default=u"Answer-date of the ticket"))),

        #Attachment
        FileField(
            name='attachment',
            storage=AttributeStorage(),
            widget=FileWidget(
                label=_(u'label_attachment', default=u"Attachment"),
                description=_(
                    u'help_attachment',
                    default=u"You may optionally upload a file attachment. " +
                    "Please do not upload unnecessarily large files."))),

        #References for Atachments
        ReferenceField(
            name='attachments',
            allowed_types=('TicketAttachment'),
            multiValued=1,
            schemata='default',
            relationship='TicketAttachment',

            widget=ReferenceBrowserWidget(
                label=_(u'label_attachments', default=u"Attachments"),
                allow_browse=True,
                show_results_without_query=True,
                restrict_browsing_to_startup_directory=True,
                base_query={
                    "portal_type": "TicketAttachment",
                    "sort_on": "sortable_title"},
                visible={'view': 'visible', 'edit': 'invisible'})),

        #References
        ReferenceField(
            name='ticketReferences',
            multiValued=1,
            schemata='default',
            relationship='TicketBox',

            widget=ReferenceBrowserWidget(
                label=_(u'label_references', default=u"References"),
                allow_browse=True,
                show_results_without_query=False,
                restrict_browsing_to_startup_directory=False)),

        ))



TicketSchema['description'] = atapi.TextField(
    name='description',
    default='',
    searchable=True,
    accessor="Description",

    # Keep the original storage for backwards compatiblity:
    storage=TicketSchema['description'].storage,

    default_content_type='text/html',
    allowable_content_types=('text/html',),
    validators=('isTidyHtmlWithCleanup', ),
    default_output_type='text/x-html-safe',
    default_input_type='text/html',

    widget = atapi.RichWidget(
        label=_(u"label_description",
                default=u"Description"),
        rows=30))

schemata.finalizeATCTSchema(TicketSchema, moveDiscussion=False)


# Hide all unimportant fields except default-schamata-fields
for field in TicketSchema.keys():
    if TicketSchema[field].schemata != 'default':
        TicketSchema[field].write_permission = ManagePortal


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
        for id_ in parent.objectIds():
            try:
                intId = int(id_)
                maxId = max(maxId, intId)
            except (TypeError, ValueError):
                pass
        return str(maxId + 1)

    def default_due_date(self):
        """ Return a default due-date (9.00 Clock in 14 days) """

        a = DateTime() + 14
        return DateTime(a.year(), a.month(), a.day(), 9, 00)

    def default_answer_date(self):
        """ Return a default answer-date (9.00 Clock in 14 days) """

        return self.default_due_date()

    def assignable_users(self):
        """
        Get the managers available as a DisplayList. The first item is 'None',
        with a key of '(UNASSIGNED)'.
        """

        return aq_parent(self).assignable_users()

    security.declarePublic('canSetDefaultPage')
    def canSetDefaultPage(self):
        return False


registerType(Ticket, PROJECTNAME)
