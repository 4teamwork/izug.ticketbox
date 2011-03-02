"""Definition of the Ticket Box content type
"""

from zope.interface import implements

from Products.Archetypes.atapi import Schema, registerType, ATFieldProperty
from Products.Archetypes.atapi import StringField, StringWidget
from Products.Archetypes.atapi import TextField, TextAreaWidget
from Products.Archetypes.atapi import LinesField, LinesWidget
from Products.Archetypes.atapi import SelectionWidget
from Products.Archetypes.atapi import BooleanField, BooleanWidget

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
            label="Ticketbox description",
            description="Describe the purpose of this Ticketbox",
        ),
        required=True,
        searchable=True
    ),
    #Individual Identifier
    StringField(
         name='individual_identifier',
         widget=StringWidget(
             label=_(u"Individual identifier"),
             description=(u"Enter a individual identifier (max 7 positions)"),
         ),
         searchable=True
     ),

    DataGridField('DemoField',
          searchable = True,
          columns=("column1", "column2", "select_sample"),
          widget = DataGridWidget(
            columns={
                 'column1' : Column("Toholampi city rox"),
                 'column2' : Column("My friendly name"),
                 'select_sample' : SelectColumn("Friendly name", vocabulary="getSampleVocabulary")
                  },
         ),
      ),

      DataGridField(
           name='availableAreas',
           default=({'id' : 'ui', 'title' : 'User interface', 'description' : 'User interface issues'}, {'id' : 'functionality', 'title' : 'Functionality', 'description' : 'Issues with the basic functionality'}, {'id' : 'process', 'title' : 'Process', 'description' : 'Issues relating to the development process itself'}),
           widget=DataGridWidget(
               label="Areas",
               description="Enter the issue topics/areas for this tracker.",
               column_names=('Short name', 'Title', 'Description'),
           ),
           allow_empty_rows=False,
           required=True,
           validators=('isDataGridFilled', ),
           columns=('id', 'title', 'description',)
       ),

       DataGridField(
           name='availableIssueTypes',
           default=({'id' : 'bug', 'title' : 'Bug', 'description' : 'Functionality bugs in the software'}, {'id' : 'feature', 'title' : 'Feature', 'description' : 'Suggested features'}, {'id' : 'patch', 'title' : 'Patch', 'description' : 'Patches to the software'}),
           widget=DataGridWidget(
               label="Issue types",
               description="Enter the issue types for this tracker.",
               column_names=('Short name', 'Title', 'Description',),
           ),
           allow_empty_rows=False,
           required=True,
           validators=('isDataGridFilled',),
           columns=('id', 'title', 'description')
       ),

       LinesField(
           name='availableSeverities',
           default=['Critical', 'Important', 'Medium', 'Low'],
           widget=LinesWidget(
               label="Available severities",
               description="Enter the different type of issue severities that should be available, one per line.",
           ),
           required=True
       ),

       StringField(
           name='defaultSeverity',
           default='Medium',
           widget=SelectionWidget(
               label="Default severity",
               description="Select the default severity for new issues.",
           ),
           enforceVocabulary=True,
           vocabulary='getAvailableSeverities',
           required=True
       ),

       LinesField(
           name='availableReleases',
           widget=LinesWidget(
               label="Available releases",
               description="Enter the releases which issues can be assigned to, one per line. If no releases are entered, issues will not be organised by release.",
           ),

       ),

       LinesField(
           name='managers',
           widget=LinesWidget(
               label="Tracker managers",
               description="Enter the user ids of the users who will be allowed to manage this tracker, one per line.",
           ),
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
    def getSampleVocabulary(self):
        """
        """
        """ Get list of possible taggable features from ATVocabularyManager """
        return DisplayList(

            (("sample", "Sample value 1",),
            ("sample2", "Sample value 2",),))




registerType(TicketBox, PROJECTNAME)
