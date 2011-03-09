from izug.ticketbox.browser.ticketbox_baseview import TabbedTicketBoxBaseView

class TicketBoxViewMyTickets(TabbedTicketBoxBaseView):

    types = 'Ticket'
    #this is a attribute in the DataGrid States from TicketBox ContentType
    filter_state = "show_in_my_tickets"
    filter_my_tickets = True
    sort_on = 'getId'
    columns = None
