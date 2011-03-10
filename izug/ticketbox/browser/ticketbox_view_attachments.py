from izug.ticketbox.browser.ticketbox_baseview import TabbedTicketBoxBaseView
from izug.ticketbox import ticketboxMessageFactory as _
from izug.arbeitsraum.browser.views import izug_files_linked

class TicketBoxViewAttachments(TabbedTicketBoxBaseView):

    types = 'TicketAttachment'
    #this is a attribute in the DataGrid States from TicketBox ContentType
    sort_on = 'getId'
    columns = None

    def __init__(self, context, request):
        super(TicketBoxViewAttachments, self).__init__(context, request)

        self.columns = ({'column':'Type',
                        'column_title':_(u"Type"),
                        'sort_index':'getContentType',

                        },
                        {'column':'Title',
                        'column_title':_(u"Title"),
                        'sort_index': 'sortable_title',
                        'transform':izug_files_linked,
                        },
                        )
