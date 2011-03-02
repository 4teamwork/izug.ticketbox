"""Definition of the Ticket Box content type
"""

from zope.interface import implements

from Products.Archetypes.atapi import Schema, registerType
from Products.Archetypes.atapi import StringField, StringWidget
from Products.Archetypes.atapi import TextField, TextAreaWidget

from Products.DataGridField import DataGridField, DataGridWidget

from Products.Archetypes.atapi import ATFieldProperty

from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

from izug.ticketbox import ticketboxMessageFactory as _

from izug.ticketbox.interfaces import ITicketBox
from izug.ticketbox.config import PROJECTNAME

from transaction import savepoint

TicketBoxSchema = folder.ATBTreeFolderSchema.copy() + Schema((

    # -*- Your Archetypes field definitions here ... -*-

    #Title
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
    #Individual Identifier
    StringField(
             name='individual_identifier',
             widget=StringWidget(
                 label=_(u"Individual identifier"),
                 description=_(u"Enter a individual identifier (max 7 positions)"),
                 maxlength = 7,
             ),
             searchable=True
    ),
     #Available Status
    DataGridField(
          name = 'availableStatus',
          searchable = True,
          allow_empty_rows = False,
          default = (
            {'id' : 'id_open', 'title' : _(u"Open")},
            {'id' : 'id_at_work', 'title' : _(u"At work")},
            {'id' : 'id_rejected', 'title' : _(u"Rejected")},
            {'id' : 'id_to_test', 'title' : _(u"To test")},
            {'id' : 'id_completed', 'title' : _(u"Completed")},
            {'id' : 'id_moved', 'title' : _(u"Moved")},
            ),
          widget = DataGridWidget(
            visible={'view': 'invisible', 'edit': 'visible'},
            label = _(u"Define a status"),
            description = _(u"add or delete possible status-information"),
            column_names = (_(u"status_id"), _(u"status_name")),
         ),
         columns = ("id", "title"),
      ),
      #Available Releases
        DataGridField(
                   name='availableReleases',
                   widget=DataGridWidget(
                       visible={'view': 'invisible', 'edit': 'visible'},
                       label=_(u"Available Releases"),
                       description=_(u"Enter the Available Releases for this tracker."),
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
                      description=_(u"Enter the different type of issue severities that should be available, one per line."),
                      column_names=(_(u'Severities_id'), _(u'Severities_title')),
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
                     description=_(u"Enter the issue topics/areas for this tracker."),
                     column_names=(_(u'Areas_id'), _(u'Areas_title')),
                 ),
                 allow_empty_rows=False,
                 required=True,
                 columns=('id', 'title')
      ),

))


schemata.finalizeATCTSchema(
    TicketBoxSchema,
    folderish=True,
    moveDiscussion=False
)




class TicketBox(folder.ATBTreeFolder):
    """Description of the Example Type"""
    implements(ITicketBox)

    meta_type = "TicketBox"
    schema = TicketBoxSchema

def renameIdAfterCreation(obj, event):

       # #save datagrid to change ids
       # availableStatus = obj.getavailableStatus()
       # availableReleases = obj.getavailableReleases()
       # availableSeverities = obj.getavailableSeverities()
       # availableAreas = obj.getavailableAreas()
       #
       # #change id from availableStatus
       # for row in availableStatus:
       #     name = row['name']

       # Can't rename without a subtransaction commit when using
       # portal_factory!
       savepoint(optimistic=True)

registerType(TicketBox, PROJECTNAME)
