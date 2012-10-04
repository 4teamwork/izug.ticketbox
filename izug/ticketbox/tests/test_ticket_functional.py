from izug.ticketbox.tests.base import TicketboxFunctionalTestCase
import unittest2 as unittest
from Products.Five.testbrowser import Browser
from Products.PloneTestCase.setup import portal_owner, default_password
from zope.annotation.interfaces import IAnnotations


class TestFunctionalTickets(TicketboxFunctionalTestCase):

    def test_view(self):
        browser = Browser()
        ticketbox_url = self.ticketbox.absolute_url()
        browser.open(ticketbox_url)
        browser.getControl(name='__ac_name').value = portal_owner
        browser.getControl(name='__ac_password').value = default_password
        browser.getControl(name='submit').click()
        browser.open(ticketbox_url+ '/folder_factories')
        button = browser.getControl(name="url")
        button.value = button.options
        browser.getControl(name="form.button.Add").click()
        browser.getControl(name="title").value = "Testissue"
        browser.getControl(name="form.button.save").click()
        self.assertEqual('Submitted at' in browser.contents, True)
        browser.getControl(name="state").value = [browser.getControl(name="state").options[1]]
        browser.getControl(name="priority").value = [browser.getControl(name="priority").options[1]
                                                     ]
        browser.getControl(name="submit").click()
        self.assertEqual('<td>Show My Tickets</td>' in browser.contents, True)
        self.assertEqual('<td>Low</td>' in browser.contents, True)
        ticket = self.ticketbox['1']
        annotations = IAnnotations(ticket)
        response = annotations['izug.ticketbox.responses'][0]
        self.assertEqual(response.changes[0]['before'], u'Test Id Priority')
        self.assertEqual(response.changes[1]['before'], u'Test Id State')
        self.assertEqual(response.changes[0]['after'], u'Low')
        self.assertEqual(response.changes[1]['after'], u'Show My Tickets')


def test_suite():
    """This sets up a test suite that actually runs the tests in the class
    above
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestFunctionalTickets))
    return suite
