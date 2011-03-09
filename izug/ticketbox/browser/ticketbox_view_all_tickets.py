from izug.arbeitsraum.browser.views import izug_files_linked
from izug.ticketbox.browser.ticketbox_baseview import TabbedTicketBoxBaseView

class TicketBoxViewAllTickets(TabbedTicketBoxBaseView):

    types = 'Ticket'
    #this is a attribute in the DataGrid States from TicketBox ContentType
    filter_state = "show_in_all_tickets"
    sort_on = 'getId'
    columns = (
                 ('getId', 'getId',),
                 ('Title', 'sortable_title', izug_files_linked),
                 ('responsibleManager', 'responsibleManager',),
                 ('State', 'State', ),
                 ('Due_date', 'Due_date', ),
                 ('Priority', 'Priority', ),
                 ('Area', 'Area', ),
                 )

