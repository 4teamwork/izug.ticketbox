from ftw.builder import Builder
from ftw.builder import create
from izug.ticketbox.testing import TICKETBOX_FUNCTIONAL_TESTING
from izug.ticketbox.tests import helpers
from plone.app.testing import TEST_USER_NAME, TEST_USER_PASSWORD
from plone.testing.z2 import Browser
from StringIO import StringIO
from unittest2 import TestCase
import transaction


class TestAttachmentCreation(TestCase):

    layer = TICKETBOX_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestAttachmentCreation, self).setUp()

        portal = self.layer['portal']
        helpers.login_as_manager(portal)

        self.ticketbox = helpers.create_ticketbox(portal)

        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False
        self.browser.addHeader('Authorization', 'Basic %s:%s' % (
                TEST_USER_NAME, TEST_USER_PASSWORD,))

        transaction.commit()

    def test_attachment_creation(self):
        ticketbox = create(Builder('ticket box')
                           .titled('THe Ticket Box'))

        ticket = create(Builder('ticket')
                        .titled('The Ticket')
                        .within(ticketbox))

        self.browser.open(ticket.absolute_url() + '/folder_factories')
        self.browser.getControl('TicketAttachment').click()
        self.browser.getControl(name='form.button.Add').click()

        file_field = self.browser.getControl(name="file_file")
        file_field.add_file(
            StringIO('GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\x00\x00'
                            '\x00!\xf9\x04\x04\x00\x00\x00\x00,\x00\x00\x00'
                            '\x00\x01\x00\x01\x00\x00\x02\x02\x01\x00;'),
            'image/gif',
            'peter.gif')
        self.browser.getControl(name="form.button.save").click()
        self.assertEqual(
            self.browser.url,
            'http://nohost/plone/the-ticket-box/the-ticket/peter.gif/view')
