from baseview import TabbedTicketBoxBaseView


class TicketBoxViewAllTickets(TabbedTicketBoxBaseView):

    types = 'Ticket'
    #this is a attribute in the DataGrid States from TicketBox ContentType
    filter_state = "show_in_all_tickets"
    columns = None
