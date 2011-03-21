import unittest
from izug.ticketbox.tests.base import TicketBoxTestCase
from zope.component import getMultiAdapter


class TestTicketBox(TicketBoxTestCase):

    def afterSetUp(self):
        super(TestTicketBox, self).afterSetUp()

    def beforeTearDown(self):
        pass

    def test_required_fields(self):
        title = self.ticketbox.getField('title')
        description = self.ticketbox.getField('description')

        self.assertEquals(title.required, True)
        self.assertEquals(description.required, True)

    def test_generated_id(self):
        state = self.ticketbox.getAvailableStates()[2]['id']
        area = self.ticketbox.getAvailableAreas()[2]['id']
        release = self.ticketbox.getAvailableReleases()[2]['id']
        priority = self.ticketbox.getAvailablePriorities()[2]['id']

        self.assertEquals(state, "test-id-state")
        self.assertEquals(area, "test-id-area")
        self.assertEquals(release, "test-id-release")
        self.assertEquals(priority, "test-id-priority")

    def test_overview_view(self):

        ticketbox_view = getMultiAdapter((self.ticketbox, self.portal.REQUEST), name='tabbedview_view-Overview')
        ticket_state = ticketbox_view.getFilteredTickets(state='test_id_1')
        ticket_area = ticketbox_view.getFilteredTickets(area='test_id_1')
        ticket_priority = ticketbox_view.getFilteredTickets(priority='test_id_1')
        ticket_responsible = ticketbox_view.getFilteredTickets(responsible='testuser1')

        self.assertEquals(ticket_state[0].getObject().getState(), "test_id_1")
        self.assertEquals(ticket_area[0].getObject().getArea(), "test_id_1")
        self.assertEquals(ticket_priority[0].getObject().getPriority(), "test_id_1")
        self.assertEquals(ticket_responsible[0].getObject().getResponsibleManager(), "testuser1")

    def test_all_tickets_view(self):

        ticketbox_view = getMultiAdapter((self.ticketbox, self.portal.REQUEST), name='tabbedview_view-all_tickets')
        ticketbox_view.search(kwargs={'portal_type':'Ticket'})

        self.assertEquals(ticketbox_view.len_results, 1)

    def test_my_tickets_view(self):

        ticketbox_view = getMultiAdapter((self.ticketbox, self.portal.REQUEST), name='tabbedview_view-my_tickets')
        ticketbox_view.search(kwargs={'portal_type':'Ticket'})

        self.assertEquals(ticketbox_view.len_results, 1)



def test_suite():
    """This sets up a test suite that actually runs the tests in the class
    above
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestTicketBox))
    return suite
