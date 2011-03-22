# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from ftw.tabbedview.interfaces import ITabbedView
from izug.ticketbox import ticketboxMessageFactory as _
from izug.ticketbox.config import PROJECTNAME
from izug.ticketbox.interfaces import ITicketBox
from izug.utils.users import getAssignableUsers
from Products.Archetypes.atapi import DisplayList
from Products.Archetypes.atapi import Schema, registerType
from Products.Archetypes.atapi import StringField, StringWidget
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata
from Products.DataGridField import DataGridField, DataGridWidget
from Products.DataGridField.Column import Column
from Products.DataGridField.SelectColumn import SelectColumn
from zope.interface import implements


TicketBoxSchema = folder.ATBTreeFolderSchema.copy() + Schema((

    #Individual Identifier
    StringField(
        name='individualIdentifier',
        searchable=True,
        widget=StringWidget(
            label=_(
                u"label_individualIdentifier",
                default=u"Individual identifier"),
            description=_(
                u"help_individualIdentifier",
                default=u"Enter a individual identifier (max 7 positions)"),
            maxlength=7,
        ),
    ),

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
                    vocabulary="yes_no"),
            }
        ),
        columns=("id", "title", "show_in_all_tickets", "show_in_my_tickets"),
    ),

    #Available Releases
    DataGridField(
        name='availableReleases',
        widget=DataGridWidget(
            visible={'view': 'invisible', 'edit': 'visible'},
            label=_(u'label_availableReleases',default=u"Available Releases"),
            description=_(u'help_avialableReleases',
                default=u"Enter the Available Releases for this tracker."),
            column_names=(_(u'Releases_id'), _(u'Releases_title')),
        ),
        allow_empty_rows=False,
        columns=('id', 'title')
    ),

    #Available Priorities
    DataGridField(
        name='availablePriorities',
        widget=DataGridWidget(
            visible={'view': 'invisible', 'edit': 'visible'},
            label=_(u'label_availablePriorities', u"Available priorities"),
            description=(_(u'help_availablePriorities',
                default=u"Enter the different type of issue severities" +
                " that should be available, one per line.")
            ),
            column_names=(
                _(u'Priorities_id'),
                _(u'Priorities_title')),
            ),
        allow_empty_rows=False,
        columns=('id', 'title'),
    ),

    #Available Areas
    DataGridField(
        name='availableAreas',
        widget=DataGridWidget(
            visible={'view': 'invisible', 'edit': 'visible'},
            label=_(u'label_Areas',default=u"Areas"),
            description=(
                _(u'help_areas',default=u"Enter the issue topics/areas for this tracker.")
            ),
            column_names=(
                _(u'Areas_id'),
                _(u'Areas_title')),
            ),
        allow_empty_rows=False,
        columns=('id', 'title'),
    ),
))

TicketBoxSchema['description'].required = True


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

        users = getAssignableUsers(self, 'Contributor', show_contacts=False)
        users.insert(0, ['(UNASSIGNED)', _(u'None')])
        return users

    def yes_no(self):
        """return displaylist with two static rows
        contents: yes and no
        """
        return DisplayList((
            ("1", _(u"yes")),
            ("0", _(u"no")),
            ))

registerType(TicketBox, PROJECTNAME)
