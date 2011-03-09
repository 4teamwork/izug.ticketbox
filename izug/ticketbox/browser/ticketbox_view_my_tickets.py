from izug.arbeitsraum.browser.views import izug_files_linked
from izug.ticketbox.browser.ticketbox_baseview import TabbedTicketBoxBaseView, readable_author
from ftw.table import helper
from izug.ticketbox import ticketboxMessageFactory as _

class TicketBoxViewMyTickets(TabbedTicketBoxBaseView):

    types = 'Ticket'
    #this is a attribute in the DataGrid States from TicketBox ContentType
    filter_state = "show_in_my_tickets"
    sort_on = 'getId'
    columns = None

    def __init__(self, context, request):
        super(TicketBoxViewMyTickets, self).__init__(context, request)

        self.columns = ({'column':'getId',
                         'column_title':_(u"Id"),
                         },
                         {'column':'Title',
                         'column_title':_(u"Title"),
                         'transform':izug_files_linked,
                         },
                         {'column':'responsibleManager',
                         'column_title':_(u"responsibleManager"),
                         'transform':readable_author,
                         },
                         {'column':'State',
                         'column_title':_(u"State"),
                         'transform':self.map_state,
                         },
                         {'column':'Due_date',
                         'column_title':_(u"Due_Date"),
                         'transform':helper.readable_date_time_text,
                         },
                         {'column':'Priority',
                         'column_title':_(u"Priority"),
                         'transform':self.map_priority,
                         },
                         {'column':'Area',
                         'column_title':_(u"Area"),
                         'transform':self.map_area,
                         },
                         )
