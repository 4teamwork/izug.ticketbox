from ftw.builder import Builder
from ftw.builder import create
from izug.ticketbox.testing import TICKETBOX_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import setRoles
from unittest2 import TestCase



class TestReferenceStartupDirectory(TestCase):

    layer = TICKETBOX_INTEGRATION_TESTING

    def setUp(self):
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)

    def test_startup_directory_is_current_context(self):
        ticketbox = create(Builder('ticket box')
                           .titled('THe Ticket Box'))

        ticket = create(Builder('ticket')
                        .titled('The Ticket')
                        .within(ticketbox))

        self.assertEquals('the-ticket-box/the-ticket',
                          ticket.getReferenceStartupDirectory())
