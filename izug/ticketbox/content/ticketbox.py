from AccessControl import ClassSecurityInfo
from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata
from Products.Archetypes.atapi import ComputedField, MultiSelectionWidget
from Products.Archetypes.atapi import DisplayList
from Products.Archetypes.atapi import LinesField
from Products.Archetypes.atapi import Schema, registerType
from Products.Archetypes.atapi import StringField, StringWidget
from Products.CMFCore.utils import getToolByName
from Products.DataGridField import DataGridField, DataGridWidget
from Products.DataGridField.Column import Column
from Products.DataGridField.SelectColumn import SelectColumn
from ftw.tabbedview.interfaces import ITabbedView
from izug.ticketbox import ticketboxMessageFactory as _
from izug.ticketbox.config import PROJECTNAME
from izug.ticketbox.interfaces import ITicketBox
from zope.component import queryUtility, getUtility
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory


TicketBoxSchema = folder.ATBTreeFolderSchema.copy() + Schema((

        #Individual Identifier
        StringField(
            name='individualIdentifier',
            searchable=True,

            widget=StringWidget(
                maxlength=7,
                label=_(u"label_individualIdentifier",
                        default=u"Individual identifier"),
                description=_(
                    u"help_individualIdentifier",
                    default=u"Enter a individual identifier " +
                    u"(max 7 positions)"))),

        #Available States
        DataGridField(
            name='availableStates',
            searchable=True,
            allow_empty_rows=False,

            default=(
                {'id': '',
                 'title': "offen",
                 'show_in_all_tickets': '1',
                 'show_in_my_tickets': '1',
                 },

                {'id': '',
                 'title': "in Bearbeitung",
                 'show_in_all_tickets': '1',
                 'show_in_my_tickets': '1',
                 },

                {'id': '',
                 'title': "zur\xc3\xbcckgewiesen",
                 'show_in_all_tickets': '1',
                 'show_in_my_tickets': '1',
                 },

                {'id': '',
                 'title': "zum Testen",
                 'show_in_all_tickets': '1',
                 'show_in_my_tickets': '1',
                 },

                {'id': '',
                 'title': "erledigt",
                 'show_in_all_tickets': '1',
                 'show_in_my_tickets': '0',
                 },

                {'id': '',
                 'title': "verschoben",
                 'show_in_all_tickets': '1',
                 'show_in_my_tickets': '1',
                 },
                ),

            columns=("id",
                     "title",
                     "show_in_all_tickets",
                     "show_in_my_tickets"),

            widget=DataGridWidget(
                visible={'view': 'invisible', 'edit': 'visible'},
                label=_(u"Define states"),
                description=_(u"add or delete possible state-information"),

                columns={
                    'id': Column(_(u"id")),
                    'title': Column(_(u"title")),
                    'show_in_all_tickets': SelectColumn(
                        _(u"show in 'all tickets'"),
                        # DatagridFields SelectColumn doesn not behave like an
                        # archetype field. It always does
                        # a getattr to get the vocab.
                        vocabulary="yes_no"),
                    'show_in_my_tickets': SelectColumn(
                        _(u"show in 'my tickets'"),
                        vocabulary="yes_no")})),

        #Available Releases
        DataGridField(
            name='availableReleases',
            allow_empty_rows=False,
            columns=('id', 'title'),

            widget=DataGridWidget(
                visible={'view': 'invisible', 'edit': 'visible'},
                label=_(u'label_availableReleases',
                        default=u"Available Releases"),
                description=_(u'help_avialableReleases',
                              default=u"Enter the Available Releases " +
                              u"for this tracker."),
                column_names=(_(u'Releases_id'), _(u'Releases_title')))),

        #Available Priorities
        DataGridField(
            name='availablePriorities',
            allow_empty_rows=False,
            columns=('id', 'title'),

            widget=DataGridWidget(
                visible={'view': 'invisible', 'edit': 'visible'},
                label=_(u'label_availablePriorities',
                        u"Available priorities"),
                description=_(u'help_availablePriorities',
                              default=u"Enter the different type of " +
                              u"issue severities that should be " +
                              u"available, one per line."),
                column_names=(
                    _(u'Priorities_id'),
                    _(u'Priorities_title')))),

        #Available Areas
        DataGridField(
            name='availableAreas',
            allow_empty_rows=False,
            columns=('id', 'title'),

            widget=DataGridWidget(
                visible={'view': 'invisible', 'edit': 'visible'},
                label=_(u'label_Areas', default=u"Areas"),
                description=_(u'help_areas',
                              default=u"Enter the issue topics/areas" +
                              u" for this tracker."),
                column_names=(
                    _(u'Areas_id'),
                    _(u'Areas_title')))),

        #Available Varieties
        DataGridField(
            name='availableVarieties',
            allow_empty_rows=False,
            columns=('id', 'title'),

            widget=DataGridWidget(
                label=_(u'label_Varieties', default=u"Varieties"),
                description=_(u'help_varieties',
                              default=u"Enter the issue varieties for " +
                                  u"this tracker."),
                column_names=(
                    _(u'Varieties_id'),
                    _(u'Varieties_title')))),

        ComputedField(
            name='assignable_user_ids',
            mode='wr',
            accessor='getAssignableUserIds',
            edit_accessor='getAssignableUserIds',
            mutator='setAssignableUserIds',
            vocabulary='unfilteredAssignableUsersVocabulary',
            expression='context.getAssignableUserIds()',

            widget=MultiSelectionWidget(
                format='checkbox',
                label=_(u'label_assignable_users',
                        default=u'Assignable users'),
                description=_(
                    u'help_assignable_users',
                    default=u'Select the users which should be assignable. '
                    'New users are by default searchable.'))),

        LinesField(
            name='not_assignable_user_ids',
            widget=MultiSelectionWidget(
                modes=())),

        ))


schemata.finalizeATCTSchema(
    TicketBoxSchema,
    folderish=True,
    moveDiscussion=False,
    )


class TicketBox(folder.ATBTreeFolder):
    """A tracker-like task management system"""

    implements(ITicketBox, ITabbedView)

    meta_type = "TicketBox"
    schema = TicketBoxSchema
    security = ClassSecurityInfo()

    def assignable_users(self):
        """
        Get the managers available as a DisplayList. The first item is 'None',
        with a key of '(UNASSIGNED)'.
        """

        factory = queryUtility(IVocabularyFactory, name='assignable_users')
        if factory is None:
            factory = getUtility(IVocabularyFactory,
                                 name='plone.principalsource.Users',
                                 context=self)

        vocabulary = factory(self)

        # TODO: Use vocabulary instead of list of tuples.
        users = [('(UNASSIGNED)', _(u'None'))]

        mtool = getToolByName(self, 'portal_membership')
        assignable_userids = self.getAssignableUserIds()

        for term in vocabulary:
            member = mtool.getMemberById(term.token)
            if member is None:
                continue
            if member.getId() not in assignable_userids:
                continue
            user = member.getUser()
            #We do this the same way plone.api does.
            #  But can't use plone.api due to a bug.
            old_security_manager = getSecurityManager()
            newSecurityManager(self.REQUEST, user)
            has_permission = user.checkPermission(
                'izug.ticketbox: Add Ticket',
                self
                )
            setSecurityManager(old_security_manager)
            if member and has_permission:
                title = term.title
                if not title:
                    title = term.value
                users.append((term.token, title))

        return users

    def getAssignableUserIds(self):
        """Returns a list of userids which are currently assignable.
        This respects the configuration whether the assigning of the user
        is enabled.
        """

        not_assignable = self.Schema().getField(
            'not_assignable_user_ids').get(self)

        userids = []
        for userid, title in self.unfilteredAssignableUsersVocabulary():
            if userid not in not_assignable:
                userids.append(userid)
        return userids

    def setAssignableUserIds(self, userids):
        """Select users from the assignable_users vocabulary which should by
        selectable.
        This works by storing the ones which are not selectable for ensuring
        that new ones automatically are selectable.
        """

        assignable_userids = userids or []

        not_assignable_userids = []
        for userid, title in self.unfilteredAssignableUsersVocabulary():
            if userid not in assignable_userids:
                not_assignable_userids.append(userid)

        self.Schema().getField('not_assignable_user_ids').set(
            self, not_assignable_userids)

    def unfilteredAssignableUsersVocabulary(self):
        """Returns a list of userid / title tuples with all users which
        are possible assignable users. It is not filtered by the
        configuration whether the users are currently enabled assignable
        users.
        """
        factory = queryUtility(IVocabularyFactory, name='assignable_users')

        if factory is None:
            factory = getUtility(IVocabularyFactory,
                                 name='plone.principalsource.Users',
                                 context=self)
            terms = factory(self)
        else:
            terms = factory(self, membersonly=True)
        values = []
        for term in terms:
            values.append((term.token, term.title))
        return values

    def yes_no(self):
        """return displaylist with two static rows
        contents: yes and no
        """
        return DisplayList((
                ("1", _(u"yes")),
                ("0", _(u"no")),
                ))

    security.declarePublic('canSetDefaultPage')
    def canSetDefaultPage(self):
        return False


registerType(TicketBox, PROJECTNAME)
