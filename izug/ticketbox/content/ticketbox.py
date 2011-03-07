"""Definition of the Ticket Box content type
"""

from zope.interface import implements

from Products.Archetypes.atapi import Schema, registerType
from Products.Archetypes.atapi import StringField, StringWidget
from Products.Archetypes.atapi import DisplayList

from Products.DataGridField import DataGridField, DataGridWidget
from Products.DataGridField.SelectColumn import SelectColumn
from Products.DataGridField.Column import Column

from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

from izug.ticketbox import ticketboxMessageFactory as _
from izug.ticketbox.interfaces import ITicketBox
from izug.ticketbox.config import PROJECTNAME

from Products.CMFCore.utils import getToolByName
from transaction import savepoint

from izug.arbeitsraum.interfaces import IArbeitsraum
from izug.utils.users import getAssignableUsers

TicketBoxSchema = folder.ATBTreeFolderSchema.copy() + Schema((

    # -*- Your Archetypes field definitions here ... -*-

    #Individual Identifier
    StringField(
             name='individual_identifier',
             widget=StringWidget(
                 label=_(u"Individual identifier"),
                 description=_(
                    u"Enter a individual identifier (max 7 positions)"),
                 maxlength = 7,
             ),
             searchable=True
    ),

     #Available States
    DataGridField(
          name = 'availableStates',
          searchable = True,
          allow_empty_rows = False,
          default = (
           {'id' : '', 'title' : _(u"Open"), 'show_in_all_tickets' : '1', 'show_in_my_tickets' : '1'},
           {'id' : '', 'title' : _(u"At work"), 'show_in_all_tickets' : '1', 'show_in_my_tickets' : '1'},
           {'id' : '', 'title' : _(u"Rejected"), 'show_in_all_tickets' : '1', 'show_in_my_tickets' : '1'},
           {'id' : '', 'title' : _(u"To test"), 'show_in_all_tickets' : '1', 'show_in_my_tickets' : '1'},
           {'id' : '', 'title' : _(u"Completed"), 'show_in_all_tickets' : '1', 'show_in_my_tickets' : '0'},
           {'id' : '', 'title' : _(u"Moved"), 'show_in_all_tickets' : '1', 'show_in_my_tickets' : '1'},
           ),
          widget = DataGridWidget(
            visible={'view': 'invisible', 'edit': 'visible'},
            label = _(u"Define states"),
            description = _(u"add or delete possible state-information"),
            columns = {
                'id' : Column(_(u"id")),
                'title' : Column(_(u"title")),
                'show_in_all_tickets' : SelectColumn(_(u"show in 'all tickets'"), vocabulary="get_yes_or_no"),
                'show_in_my_tickets' : SelectColumn(_(u"show in 'my tickets'"), vocabulary="get_yes_or_no"),
            }

         ),
         columns = ("id", "title", "show_in_all_tickets", "show_in_my_tickets"),
      ),
      #Available Releases
        DataGridField(
                   name='availableReleases',
                   widget=DataGridWidget(
                       visible={'view': 'invisible', 'edit': 'visible'},
                       label=_(u"Available Releases"),
                       description=_(
                           u"Enter the Available Releases for this tracker."),
                       column_names=(_(u'Releases_id'), _(u'Releases_title')),
                   ),
                   allow_empty_rows=False,
                   required=False,
                   columns=('id', 'title')
               ),
      #Available Severities
       DataGridField(
                  name='availableSeverities',
                  widget=DataGridWidget(
                      visible={'view': 'invisible', 'edit': 'visible'},
                      label=_(u"Available severities"),
                      description=_(
                            u"Enter the different type of issue severities" +
                            " that should be available, one per line."),
                      column_names=(
                        _(u'Severities_id'),
                        _(u'Severities_title')),
                  ),
                  allow_empty_rows=False,
                  required=False,
                  columns=('id', 'title'),
              ),
      #Available Areas
      DataGridField(
                 name='availableAreas',
                 widget=DataGridWidget(
                     visible={'view': 'invisible', 'edit': 'visible'},
                     label=_(u"Areas"),
                     description=_(
                        u"Enter the issue topics/areas for this tracker."),
                     column_names=(_(u'Areas_id'), _(u'Areas_title')),
                 ),
                 allow_empty_rows=False,
                 required=True,
                 columns=('id', 'title'),
      ),
))


schemata.finalizeATCTSchema(
    TicketBoxSchema,
    folderish=True,
    moveDiscussion=False
)




class TicketBox(folder.ATBTreeFolder):
    """Description of the Example Type"""
    implements(ITicketBox, IArbeitsraum)

    meta_type = "TicketBox"
    schema = TicketBoxSchema

    def get_assignable_users(self):
        """
        Get the managers available as a DisplayList. The first item is 'None',
        with a key of '(UNASSIGNED)'.
        """

        users = getAssignableUsers(self,'Reader')
        users.insert(0,['(UNASSIGNED)', _(u'None')])
        return users

    def get_yes_or_no(self):
        """
        Return a DisplayList with yes or no (used for a dropdown)
        """
        return DisplayList(

            (
            ("1", _(u"yes"),),
            ("0", _(u"no"),),
            ))


def renameIdAfterCreation(obj, event):

    plone_tool = getToolByName(obj, 'plone_utils', None)
    datagrid = []

    #save datagrid to change ids
    datagrid.append(obj.getAvailableStates())
    datagrid.append(obj.getAvailableReleases())
    datagrid.append(obj.getAvailableSeverities())
    datagrid.append(obj.getAvailableAreas())

    #change id from datagrids
    for dg in datagrid:
        for row in dg:
            if not row['id']:
                name = row['title']
                row['id'] =  plone_tool.normalizeString(name)

    # Can't rename without a subtransaction commit when using
    # portal_factory!
    savepoint(optimistic=True)

registerType(TicketBox, PROJECTNAME)
