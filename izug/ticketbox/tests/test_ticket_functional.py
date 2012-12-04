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

    def test_view(self):
        ticketbox_url = self.ticketbox.absolute_url()

        self.browser.open(ticketbox_url + '/folder_factories')
        self.browser.getControl('Ticket').click()
        self.browser.getControl('Add').click()

        self.browser.getControl('Title').value = "Testissue"
        self.browser.getControl('Save').click()
        self.assertEqual('Submitted at' in self.browser.contents, True)

        self.browser.getControl(name="state").value = [
            self.browser.getControl(name="state").options[1]]
        self.browser.getControl(name="priority").value = [
            self.browser.getControl(name="priority").options[1]]
        self.browser.getControl(name="submit").click()
        self.assertIn('<td>Show My Tickets</td>',
                         self.browser.contents)
        self.assertIn('<td>Low</td>', self.browser.contents)

        ticket = self.ticketbox['1']
        annotations = IAnnotations(ticket)
        response = annotations['izug.ticketbox.responses'][0]

        self.assertEqual(response.changes[0]['before'], u'High')
        self.assertEqual(response.changes[1]['before'], u'Show All Tickets')
        self.assertEqual(response.changes[0]['after'], u'Low')
        self.assertEqual(response.changes[1]['after'], u'Show My Tickets')
