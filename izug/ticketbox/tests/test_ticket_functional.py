from izug.ticketbox.testing import TICKETBOX_FUNCTIONAL_TESTING
from izug.ticketbox.tests import helpers
from plone.app.testing import TEST_USER_NAME, TEST_USER_PASSWORD
from plone.testing.z2 import Browser
from unittest2 import TestCase
from zope.annotation.interfaces import IAnnotations
import transaction


class TestFunctionalTickets(TestCase):

    layer = TICKETBOX_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestFunctionalTickets, self).setUp()

        portal = self.layer['portal']
        helpers.login_as_manager(portal)

        self.ticketbox = helpers.create_ticketbox(portal)

        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False
        self.browser.addHeader('Authorization', 'Basic %s:%s' % (
                TEST_USER_NAME, TEST_USER_PASSWORD,))

        transaction.commit()

    def tearDown(self):
        helpers.remove_obj(self.ticketbox)
        helpers.logout_manager(self.layer['portal'])
        super(TestFunctionalTickets, self).tearDown()
