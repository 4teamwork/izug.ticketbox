from izug.ticketbox.testing import TICKETBOX_INTEGRATION_TESTING
from izug.ticketbox.tests import helpers
from ftw.builder import create, Builder
from plone.app.testing import login
from unittest2 import TestCase


class TestSubTicket(TestCase):

    layer = TICKETBOX_INTEGRATION_TESTING

    def setUp(self):
        super(TestSubTicket, self).setUp()

        self.portal = self.layer['portal']

        helpers.login_as_manager(self.portal)
        self.ticketbox = helpers.create_ticketbox(self.portal)
        self.ticket = helpers.create_ticket(self.ticketbox)
        self.subticket = helpers.create_ticket(self.ticket, 'SubTicket')

    def tearDown(self):
        helpers.remove_obj(self.ticketbox)
        helpers.logout_manager(self.layer['portal'])
        super(TestSubTicket, self).tearDown()

    def test_delegated_ticket_tab_view(self):
        """
        This test makes sure that the authenticated user can only see the
        subtickets he has created, not the subtickets created by other users.
        """
        contents = self._get_view_contents()
        self.assertEquals(1, len(contents), "Exactly one subticket expected.")

        helpers.logout_manager(self.portal)
        hugo = create(Builder('user').with_roles('Manager'))
        login(self.portal, hugo.getId())
        contents = self._get_view_contents()
        self.assertEquals(0, len(contents), "Zero subtickets expected.")

    def _get_view_contents(self):
        view = self.subticket.restrictedTraverse('tabbedview_view-issued_subtickets')
        view.update()
        contents = view.contents
        return contents