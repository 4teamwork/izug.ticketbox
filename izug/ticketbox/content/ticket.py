from AccessControl import ClassSecurityInfo
from Acquisition import aq_parent
from Acquisition import aq_inner
from borg.localrole.interfaces import IFactoryTempFolder
from DateTime import DateTime
from izug.ticketbox import ticketboxMessageFactory as _
from izug.ticketbox.config import PROJECTNAME
from izug.ticketbox.hashtag import create_hash_tag_links
from izug.ticketbox.interfaces import ITicket
from izug.ticketbox.interfaces import ITicketReferenceStartupDirectory
from izug.ticketbox.interfaces import IResponseContainer
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
from zope.schema.interfaces import IVocabularyFactory
from zope.component import getUtility
from zope.component import getMultiAdapter
from Products.Archetypes import atapi
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.utils import DisplayList


TicketSchema = schemata.ATContentTypeSchema.copy() + Schema((

    atapi.TextField(
        name='client',
        widget=atapi.TextAreaWidget(
            label=_(u"label_client", default=u"Client"),
            description=_(u"help_client",
                          default=u"Name, Address, Phone or E-Mail"),
        ),
        default_content_type='text/plain',
        allowable_content_types=('text/plain',),
        default_output_type='text/html',
    ),

    DateTimeField(
        name='submissionDate',
        default_method=DateTime,
        required=True,
        validators=('isValidDate'),
        widget=CalendarWidget(
            label=_(u"label_submision_date", default=u"Submission Date"),
            description=_(u"help_submission_date", default=u""),
        ),
    ),

    # Due-Date (default: x + 14 days)
    DateTimeField(
        name='dueDate',
        default_method='default_due_date',
        required=True,
        validators=('isValidDate'),
        widget=CalendarWidget(
            label=_(u"label_duedate", default=u"Due Date"),
        ),
    ),

    # State
    StringField(
        name='state',
        vocabulary_factory='ticketbox_values_states',
        widget=SelectionWidget(
            format="select",
            label=_(u"label_state", default=u"State"),
            description=_(u"help_state",
                          default=u"Define Which State the Ticket has"))),

    # Priority
    StringField(
        name='priority',
        vocabulary_factory='ticketbox_values_priorities',
        widget=SelectionWidget(
            condition='python:here.has_items("ticketbox_values_priorities")',
            format="select",
            label=_(u"label_select_priority",
                    default=u"Select Priority"),
            description=_(u"help_priority",
                          default=u"Select the Priority"))),

    StringField(
        name='classification',
        vocabulary='getAvailableWorkflowStates',
        required=True,
        default='bve_ticket_workflow--STATUS--offentlich',
        widget=SelectionWidget(
            label=_(u"label_classification", default=u"Classification"),
        ),
    ),

    # Area
    StringField(
        name='area',
        vocabulary_factory='ticketbox_values_areas',
        widget=SelectionWidget(
            condition='python:here.has_items("ticketbox_values_areas")',
            format="select",
            label=_(u"label_select_area", default=u'Select Area'),
        ),
    ),

    # Variety
    StringField(
        name='variety',
        vocabulary_factory='ticketbox_values_varieties',
        widget=SelectionWidget(
            condition='python:here.has_items("ticketbox_values_varieties")',
            label=_(u"label_select_variety",
                    default=u'Select Variety'),
            description=_(
                u'help_variety',
                default=u'Select the Variety of the ticket'),
            format="select")),

    # Releases
    # XXX: RENAME TO RELEASE
    StringField(
        name='releases',
        vocabulary_factory='ticketbox_values_releases',
        widget=SelectionWidget(
            condition='python:here.has_items("ticketbox_values_releases")',
            format="select",
            label=_(u'label_select_release', default=u'Select Release'),
            description=_(u'help_release',
                          default=u'Select the Release of the ticket'))),

    # Watched in release
    StringField(
        name='watchedRelease',
        vocabulary_factory='ticketbox_values_releases',
        widget=SelectionWidget(
            condition='python:here.has_items("ticketbox_values_releases")',
            format="select",
            label=_(u'label_select_watchedRelease',
                    default=u'Select watched in release'),
            description=_(
                u'help_watchedRelease',
                default=u'Select in which release you watched it'))),

    # Responsible
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

    # Answer-date (default: x + 14 days)
    DateTimeField(
        name='answerDate',
        default_method='default_answer_date',
        widget=CalendarWidget(
            label=_(u'label_AnswerDate',
                    default=u"Answer Date"),
            ),
    ),

    # Attachment
    FileField(
        name='attachment',
        storage=AttributeStorage(),
        widget=FileWidget(
            label=_(u'label_attachment', default=u"Attachment"),
            description=_(
                u'help_attachment',
                default=u"You may optionally upload a file attachment. " +
                "Please do not upload unnecessarily large files."))),

    # References for Atachments
    ReferenceField(
        name='attachments',
        allowed_types=('File'),
        multiValued=1,
        schemata='default',
        relationship='File',

        widget=ReferenceBrowserWidget(
            label=_(u'label_attachments', default=u"Attachments"),
            allow_browse=True,
            show_results_without_query=True,
            restrict_browsing_to_startup_directory=True,
            base_query={
                "portal_type": "File",
                "sort_on": "sortable_title"},
            visible={'view': 'visible', 'edit': 'invisible'})),

    # References
    ReferenceField(
        name='ticketReferences',
        multiValued=1,
        schemata='default',
        relationship='TicketBox',

        widget=ReferenceBrowserWidget(
            label=_(u'label_references', default=u"References"),
            allow_browse=True,
            show_results_without_query=False,
            restrict_browsing_to_startup_directory=False,
            startup_directory_method='getReferenceStartupDirectory')),

    ))


TicketSchema['description'] = atapi.TextField(
    name='description',
    default='',
    searchable=True,
    accessor="Description",

    # Keep the original storage for backwards compatiblity:
    storage=TicketSchema['description'].storage,

    default_content_type='text/plain',  # text/x-web-intelligent
    allowable_content_types=('text/plain'),
    default_output_type='text/html',

    widget = atapi.TextAreaWidget(
        label=_(u"label_description",
                default=u"Description"),
        rows=7))

TicketSchema['title'].accessor = 'getTitle'

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

    def Title(self):
        return ' '.join((self.ticketIdentifier(), self.getTitle()))

    def ticketIdentifier(self):
        ticketbox = aq_parent(aq_inner(self))
        if ticketbox:
            identifier = ticketbox.getIndividualIdentifier()
        else:
            identifier = '-'
        year = self.getSubmissionDate().strftime('%Y')
        return '/'.join((identifier, year, self.getId()))

    def SearchableText(self, *args, **kwargs):
        return ' '.join((
                self.ticketIdentifier(),
                super(Ticket, self).SearchableText(*args, **kwargs),
                self.searchable_text_of_answers()))

    def searchable_text_of_answers(self):
        trans = getToolByName(self, 'portal_transforms')
        text = []

        for id_, response in enumerate(IResponseContainer(self)):
            text.append(trans.convertTo(
                    'text/plain',
                    response.text,
                    mimetype=response.mimetype).getData())

        return ' '.join(text)

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

    def has_items(self, voc_name):
        factory = getUtility(IVocabularyFactory, name=voc_name)
        parent = aq_parent(self)
        obj = self
        if IFactoryTempFolder.providedBy(parent):
            obj = aq_parent(aq_parent(parent))

        return len([term for term in factory(obj) if term.value])

    security.declarePrivate('getReferenceStartupDirectory')

    def getReferenceStartupDirectory(self):
        getter = getMultiAdapter((self, self.REQUEST),
                                 ITicketReferenceStartupDirectory)
        return getter.get()

    def getAvailableWorkflowStates(self):
        """Returns a list with all available workflow states for this object.
        """
        wftool = getToolByName(self, 'portal_workflow')
        wf_ids = wftool.getChainFor(self)
        wf = wftool.getWorkflowById(wf_ids[0])
        wf_states = DisplayList()
        for wf_state_id, wf_state in wf.states.objectItems():
            wf_states.add(wf_state_id, wf_state.title)
        return wf_states

    def DescriptionWithDMSLinks(self):
        utool = getToolByName(self, 'portal_url')
        desc = self.Description()
        return create_hash_tag_links(desc, utool())


registerType(Ticket, PROJECTNAME)
