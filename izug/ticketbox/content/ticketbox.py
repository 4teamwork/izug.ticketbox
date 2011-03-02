"""Definition of the Ticket Box content type
"""

from zope.interface import implements

from Products.Archetypes.atapi import Schema, registerType, ATFieldProperty
from Products.Archetypes.atapi import StringField, StringWidget
from Products.Archetypes.atapi import TextField, TextAreaWidget
# from Products.Archetypes.atapi import LinesField, LinesWidget
from Products.Archetypes.atapi import SelectionWidget
# from Products.Archetypes.atapi import BooleanField, BooleanWidget

from Products.Archetypes.public import DisplayList

from Products.DataGridField import DataGridField, DataGridWidget
from Products.DataGridField.Column import Column
from Products.DataGridField.SelectColumn import SelectColumn


from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

from izug.ticketbox import ticketboxMessageFactory as _

from izug.ticketbox.interfaces import ITicketBox
from izug.ticketbox.config import PROJECTNAME

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
    StringField(
             name='individual_identifier',
             widget=StringWidget(
                 label=_(u"Individual identifier"),
                 description=_(u"Enter a individual identifier (max 7 positions)"),
                 maxlength = 7,
             ),
             searchable=True
    ),
     #Status
    DataGridField(
          name = 'status',
          searchable = True,
          allow_empty_rows = False,
          default = (
            {'status_id' : 'id_open', 'status_name' : _(u"Open")},
            {'status_id' : 'id_at_work', 'status_name' : _(u"At work")},
            {'status_id' : 'id_rejected', 'status_name' : _(u"Rejected")},
            {'status_id' : 'id_to_test', 'status_name' : _(u"To test")},
            {'status_id' : 'id_completed', 'status_name' : _(u"Completed")},
            {'status_id' : 'id_moved', 'status_name' : _(u"Moved")},
            ),
          widget = DataGridWidget(
            label = _(u"Define a status"),
            description = _(u"add or delete possible status-information"),
            column_names = (_(u"status_id"), _(u"status_name")),
         ),
         columns = ("status_id", "status_name"),
      ),
      #Available Releases
        DataGridField(
                   name='availableReleases',
                   widget=DataGridWidget(
                       label=_(u"Available Releases"),
                       description=_(u"Enter the Available Releases for this tracker."),
                       column_names=(_(u'Id'), _(u'Title')),
                   ),
                   allow_empty_rows=False,
                   required=False,
                   columns=('id', 'title')
               ),
      #Available Severities
       DataGridField(
                  name='availableSeverities',
                  widget=DataGridWidget(
                      label=_(u"Available severities"),
                      description=_(u"Enter the different type of issue severities that should be available, one per line."),
                      column_names=(_(u'ID'), _(u'Title')),
                  ),
                  allow_empty_rows=False,
                  required=False,
                  columns=('id', 'title'),
              ),

      DataGridField(
                 name='availableAreas',
                 widget=DataGridWidget(
                     label=_(u"Areas"),
                     description=_(u"Enter the issue topics/areas for this tracker."),
                     column_names=(_(u'Short name'), _(u'Title')),
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

    # title = ATFieldProperty('title')
    # description = ATFieldProperty('description')
    # individual_identifier = ATFieldProperty('individual_identifier')
    #
    # def getSampleVocabulary(self):
    #     """
    #     """
    #     """ Get list of possible taggable features from ATVocabularyManager """
    #     return DisplayList(
    #
    #         (("sample", "Sample value 1",),
    #         ("sample2", "Sample value 2",),))
    #



registerType(TicketBox, PROJECTNAME)
