from izug.arbeitsraum.browser.views import izug_files_linked
from izug.ticketbox.browser.ticketbox_baseview import TabbedTicketBoxBaseView

class TicketBoxViewMyTickets(TabbedTicketBoxBaseView):

    types = 'Ticket'
    #this is a attribute in the DataGrid States from TicketBox ContentType
    filter_state = "show_in_my_tickets"
    sort_on = 'id'

    columns = (
               ('getId', 'sortable_title',),
               ('Title', 'sortable_title', izug_files_linked),
               ('responsibleManager', 'sortable_title',),
               ('State', 'sortable_title', ),
               ('Due_date', 'sortable_title', ),
               ('Priority', 'sortable_title', ),
               ('Area', 'sortable_title', ),
               )
