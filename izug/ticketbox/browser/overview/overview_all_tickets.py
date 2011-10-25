from baseview import TabbedTicketBoxOverviewBaseView


class TicketBoxAllTickets(TabbedTicketBoxOverviewBaseView):
    """ Overview-view for Ticketboxes.
    We use this view to list all Ticketboxes in a Plonesite
    """
    types = 'Ticket'
    columns = None
    filter_state = "show_in_all_tickets"
    sort_on = 'sortable_title'
