from izug.arbeitsraum.browser.views import izug_files_linked
from izug.ticketbox.browser.ticketbox_baseview import TabbedTicketBoxBaseView, readable_author
from ftw.table import helper

class TicketBoxViewMyTickets(TabbedTicketBoxBaseView):

    types = 'Ticket'
    #this is a attribute in the DataGrid States from TicketBox ContentType
    filter_state = "show_in_my_tickets"
    sort_on = 'getId'
    columns = None

    def __init__(self, context, request):
        super(TicketBoxViewMyTickets, self).__init__(context, request)

        self.columns = (
                     ('getId', 'getId',),
                     ('Title', 'sortable_title', izug_files_linked),
                     ('responsibleManager', 'responsibleManager',readable_author),
                     ('State', 'State', self.map_state),
                     ('Due_date', 'Due_date', helper.readable_date_time_text),
                     ('Priority', 'Priority', self.map_priority),
                     ('Area', 'Area', self.map_area),
                 )