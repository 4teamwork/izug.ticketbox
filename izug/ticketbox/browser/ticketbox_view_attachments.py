from izug.ticketbox.browser.ticketbox_baseview import TabbedTicketBoxBaseView
from izug.ticketbox import ticketboxMessageFactory as _

class TicketBoxViewAttachments(TabbedTicketBoxBaseView):

    types = 'TicketAttachment'
    #this is a attribute in the DataGrid States from TicketBox ContentType
    sort_on = 'sortable_title'
    columns = None

    def __init__(self, context, request):
        super(TicketBoxViewAttachments, self).__init__(context, request)

        self.columns = ({'column':'Type',
                        'column_title':_(u"Type"),
                        'sort_index':'getContentType',
                        'transform':self.icon,
                        },
                        {'column':'Title',
                        'column_title':_(u"Title"),
                        'sort_index': 'sortable_title',
                        'transform':self.izug_files_linked,
                        },
                        {'column':'getId',
                        'column_title':_(u"Ticketnr"),
                        'transform':self.get_attachment_ticket_nr,
                        },
                        )
