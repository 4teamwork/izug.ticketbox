from izug.ticketbox.testing import TICKETBOX_INTEGRATION_TESTING
from plone.app.testing import login, setRoles
from plone.app.testing import TEST_USER_NAME, TEST_USER_ID
from Products.CMFCore.utils import getToolByName
from unittest2 import TestCase
import os


class TestGetIcon(TestCase):

    layer = TICKETBOX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.file_ = open(
            "%s/testfile.NonsenseExtension" % os.path.split(__file__)[0], 'r'
            )
        self.mtr = getToolByName(self.portal, 'mimetypes_registry')
        ticketattachment_fti = getattr(self.portal.portal_types,
                                       'TicketAttachment')
        ticketattachment_fti.global_allow = True
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

    def test_custom_icon(self):
        self.mtr.manage_addMimeType('customimage type',
                                    ['image/x-custom-image'],
                                    ['NonsenseExtension'],
                                    'customicon.png')
        plonefile = self.portal.get(
            self.portal.invokeFactory('TicketAttachment',
                                      'myattachment',
                                      file=self.file_)
            )
        self.assertEqual('plone/customicon.png', plonefile.getIcon())

    def test_default_icon(self):
        self.mtr.manage_addMimeType('customimage type',
                                    ['image/x-custom-image'],
                                    ['NonsenseExtension'],
                                    '')
        plonefile = self.portal.get(
            self.portal.invokeFactory('TicketAttachment',
                                      'myattachment',
                                      file=self.file_)
            )
        self.assertEqual('plone/image.png', plonefile.getIcon())

    def test_contenttype_not_found(self):
        #To test the behavior of our function when a contenttype is not found
        #in mimetyperegistry we add a mimetype so everything is indexed and
        #created correctly.
        self.mtr.manage_addMimeType('customimage type',
                                    ['image/x-custom-image'],
                                    ['NonsenseExtension'], '')
        plonefile = self.portal.get(
            self.portal.invokeFactory('TicketAttachment',
                                      'myattachment',
                                      file=self.file_)
            )
        #and then we remove it again so we won't find it in the registry.
        self.mtr.manage_delObjects(['image/x-custom-image'])

        self.assertIn(plonefile.getIcon(), (
                'plone/image_icon.gif',  # Plone <= 4.3.2
                'plone/image_icon.png',  # Plone >= 4.3.3
                ))
