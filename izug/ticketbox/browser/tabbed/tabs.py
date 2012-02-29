from izug.ticketbox.browser.tabbed.base import BaseTicketListingTab


class AllTicketsTab(BaseTicketListingTab):
    """Tab listing all tickets in this ticketbox.
    """

    def get_base_query(self):
        query = super(AllTicketsTab, self).get_base_query()

        query['getState'] = [state['id']
                             for state in self.context.getAvailableStates()
                             if state['show_in_all_tickets'] == '1']

        return query


class MyTicketsTab(BaseTicketListingTab):
    """Tab listing all tickets where the current user is responsible.
    """

    def get_base_query(self):
        query = super(MyTicketsTab, self).get_base_query()

        member = self.context.restrictedTraverse('@@plone_portal_state').member()
        query['getResponsibleManager'] = member.getId()
        query['getState'] = [state['id']
                             for state in self.context.getAvailableStates()
                             if state['show_in_my_tickets'] == '1']

        return query
