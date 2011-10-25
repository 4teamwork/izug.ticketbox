from baseview import TabbedTicketBoxOverviewBaseView


class TicketBoxMyTickets(TabbedTicketBoxOverviewBaseView):
    """ Overview-view for Ticketboxes.
    We use this view to list all Ticketboxes in a Plonesite
    """
    types = 'Ticket'
    columns = None
    sort_on = 'sortable_title'
    filter_state = "show_in_my_tickets"
    filter_my_created_tickets = True
