from izug.ticketbox import ticketboxMessageFactory as _
from baseview import TabbedTicketBoxBaseView

class TicketBoxViewAttachments(TabbedTicketBoxBaseView):

    types = 'TicketAttachment'
    sort_on = 'sortable_title'
    columns = None

    def __init__(self, context, request):
        super(TicketBoxViewAttachments, self).__init__(context, request)

        self.columns = ({'column': 'Type',
                        'column_title': _(u"Type"),
                        'sort_index': 'getContentType',
                        'transform': self.icon,
                        },
                        {'column': 'Title',
                        'column_title': _(u"Title"),
                        'sort_index': 'sortable_title',
                        'transform': self.izug_files_linked,
                        },
                        {'column': 'getId',
                        'column_title': _(u"Ticketnr"),
                        'sort_index': 'sortable_ticket_references',
                        'transform': self.get_attachment_ticket_nr,
                        },
                        )
