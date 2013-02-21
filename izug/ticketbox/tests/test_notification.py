import unittest2 as unittest
from izug.ticketbox.testing import TICKETBOX_FUNCTIONAL_TESTING
from plone.testing.z2 import Browser
import transaction
from izug.ticketbox.tests import helpers
from izug.ticketbox.adapters import Response
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from Products.CMFCore.utils import getToolByName

class TestResponseNotification(unittest.TestCase):

    layer = TICKETBOX_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        helpers.login_as_manager(self.portal)
        regtool = getToolByName(self.portal, 'portal_registration')
        regtool.addMember('usera', 'usera',
                          properties={'username': 'usera',
                                      'fullname': 'fullnamea',
                                      'email': 'usera@email.com'})
        self.ticketbox = helpers.create_ticketbox(self.portal)
        self.ticketbox.manage_addLocalRoles('usera', ['Contributor', 'Manager'])
        self.ticket1 = helpers.create_ticket(self.ticketbox)
        transaction.commit()
        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False

    def test_notification_response_author(self):
        self.browser.addHeader('Authorization', 'Basic %s:%s' % (
                "usera", "usera",))
        self.browser.open(self.ticket1.absolute_url())
        self.browser.getControl("High").selected = True
        self.browser.getControl("Send notification").selected = True
        self.browser.getControl(name="submit").click()
        list_to = self.browser.getControl(name="to_list:list")
        list_to.controls[0].selected = True
        self.browser.getControl(name='form.button.Send').click()
        self.assertIn('A new Answer has been Added by <span>fullnamea</span> in the Ticketbox', self.portal.MailHost.messages[0])
