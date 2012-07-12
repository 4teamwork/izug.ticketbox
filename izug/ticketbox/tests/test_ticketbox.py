from izug.ticketbox.tests.base import TicketBoxTestCase
from zope.component import getMultiAdapter
import unittest


class TestTicketBox(TicketBoxTestCase):

    def afterSetUp(self):
        super(TestTicketBox, self).afterSetUp()

    def beforeTearDown(self):
        pass

    def test_required_fields(self):
        title = self.ticketbox.getField('title')
        description = self.ticketbox.getField('description')

        self.assertEquals(title.required, True)
        self.assertEquals(description.required, False)

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

        def get_filtered_tickets(filterid, filtervalue):
            self.portal.REQUEST.set('filterid', filterid)
            self.portal.REQUEST.set('filtervalue', filtervalue)
            view = getMultiAdapter(
                (self.ticketbox, self.portal.REQUEST),
                name='tabbedview_view-overview')
            view.update()
            contents = view.contents
            self.portal.REQUEST.set('filterid', None)
            self.portal.REQUEST.set('filtervalue', None)
            return contents

        ticket_state = get_filtered_tickets('getState', 'test_id_1')
        ticket_area = get_filtered_tickets('getArea', 'test_id_1')
        ticket_priority = get_filtered_tickets('getPriority', 'test_id_1')
        ticket_responsible = get_filtered_tickets('getResponsibleManager',
                                                  'test_user_1_')

        self.assertEquals(ticket_state[0].getObject().getState(), "test_id_1")
        self.assertEquals(ticket_area[0].getObject().getArea(), "test_id_1")
        self.assertEquals(ticket_priority[0].getObject().getPriority(),
                          "test_id_1")
        self.assertEquals(
            ticket_responsible[0].getObject().getResponsibleManager(),
            "test_user_1_")

    def test_all_tickets_view(self):
        ticketbox_view = getMultiAdapter(
            (self.ticketbox, self.portal.REQUEST),
            name='tabbedview_view-all_tickets')
        ticketbox_view.update()

        self.assertEquals(len(ticketbox_view.contents), 1)

    def test_my_tickets_view(self):
        ticketbox_view = getMultiAdapter(
            (self.ticketbox, self.portal.REQUEST),
            name='tabbedview_view-my_tickets')
        ticketbox_view.update()

        self.assertEquals(len(ticketbox_view.contents), 1)

    def test_unassigned_is_assignable(self):
        self.assertIn(
            ('(UNASSIGNED)', u'None'),
            self.ticketbox.assignable_users())

    def test_make_user_not_assignable(self):
        field = self.ticketbox.getField('assignable_user_ids')
        mutator = field.getMutator(self.ticketbox)

        self.ticketbox.manage_setLocalRoles(
            'test_user_1_', ['Contributor', 'Reader'])

        self.assertIn(
            ('test_user_1_', 'test_user_1_'),
            self.ticketbox.assignable_users())

        mutator([])
        self.assertNotIn(
            ('test_user_1_', 'test_user_1_'),
            self.ticketbox.assignable_users())

        mutator(['test_user_1_'])
        self.assertIn(
            ('test_user_1_', 'test_user_1_'),
            self.ticketbox.assignable_users())

    def test_new_user_gets_assignable_automatically(self):
        self.assertNotIn(
            ('test_user_1_', 'test_user_1_'),
            self.ticketbox.assignable_users())

        self.ticketbox.manage_setLocalRoles(
            'test_user_1_', ['Contributor', 'Reader'])

        self.assertIn(
            ('test_user_1_', 'test_user_1_'),
            self.ticketbox.assignable_users())


def test_suite():
    """This sets up a test suite that actually runs the tests in the class
    above
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestTicketBox))
    return suite
