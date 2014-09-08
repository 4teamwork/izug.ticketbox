from ftw.notification.email.interfaces import IEMailRepresentation
from ftw.notification.email.interfaces import ISubjectCreator
from izug.ticketbox.testing import TICKETBOX_FUNCTIONAL_TESTING
from izug.ticketbox.tests import helpers
from plone.testing.z2 import Browser
from Products.CMFCore.utils import getToolByName
from zope.component import getAdapter
import transaction
import unittest2 as unittest


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
        self.ticketbox.manage_addLocalRoles('usera',
                                           ['Contributor', 'Manager'])
        self.ticket1 = helpers.create_ticket(self.ticketbox)
        transaction.commit()
        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False

    def get_email_subject_prefix_from_propertysheet(self):
        portal_properties = getToolByName(self.portal, 'portal_properties')
        return portal_properties['ftw.notification-properties'].getProperty(
            'notification_email_subject')

    def test_fullname_on_ticket_notification(self):
        self.ticket1.setResponsibleManager('usera')

        email_representation = getAdapter(self.ticket1, IEMailRepresentation)
        self.assertIn('fullname', email_representation.template(),
            'The fullname of usea should appear in the mail')

    def test_subject_on_ticketbox_without_individual_identifier(self):
        self.ticketbox.setIndividualIdentifier('')
        subject = getAdapter(self.ticketbox, ISubjectCreator)

        expect = '%s %s' % (self.get_email_subject_prefix_from_propertysheet(),
                            self.ticketbox.Title())

        self.assertEquals(expect,
                          subject(self.ticketbox))

    def test_subject_on_ticketbox_with_individual_identifier(self):
        subject = getAdapter(self.ticketbox, ISubjectCreator)
        expect = '%s [%s] %s' % (
            self.get_email_subject_prefix_from_propertysheet(),
            self.ticketbox.getIndividualIdentifier(),
            self.ticketbox.Title())

        self.assertEquals(expect,
                          subject(self.ticketbox))

    def test_subject_on_ticket_without_individual_indentifier(self):
        self.ticketbox.setIndividualIdentifier('')
        subject = getAdapter(self.ticket1, ISubjectCreator)

        expect = '%s #%s - %s' % (
            self.get_email_subject_prefix_from_propertysheet(),
            self.ticket1.getId(),
            self.ticket1.Title())

        self.assertEquals(expect,
                          subject(self.ticket1))

    def test_subject_on_ticket_with_individual_indentifier(self):
        subject = getAdapter(self.ticket1, ISubjectCreator)

        expect = '%s [%s] #%s - %s' % (
            self.get_email_subject_prefix_from_propertysheet(),
            self.ticketbox.getIndividualIdentifier(),
            self.ticket1.getId(),
            self.ticket1.Title())

        self.assertEquals(expect,
                          subject(self.ticket1))
