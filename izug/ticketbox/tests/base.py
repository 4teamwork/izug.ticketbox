"""Test setup for integration and functional tests.

When we import PloneTestCase and then call setupPloneSite(), all of Plone's
products are loaded, and a Plone site will be created. This happens at module
level, which makes it faster to run each test, but slows down test runner
startup.
"""

from Products.CMFCore.utils import getToolByName
from Products.Five import zcml
from Products.PloneTestCase import PloneTestCase as ptc
from Testing import ZopeTestCase as ztc
from collective.testcaselayer.ptc import BasePTCLayer, ptc_layer
from izug.ticketbox.adapters import Response, ResponseContainer
from izug.ticketbox.handlers import generate_datagrid_column_id
import unittest2

# Mock data to be used in various tests in izug.ticketbox
MOCK_STATE = [{'id': 'test_id_1',
             'title': "Show All Tickets",
             'show_in_all_tickets': '1',
             'show_in_my_tickets': '0',
            },
            {'id': 'test_id_2',
             'title': "Show My Tickets",
             'show_in_all_tickets': '0',
             'show_in_my_tickets': '1',
            },
            {'id': '',
             'title': "Test Id State",
             'show_in_all_tickets': '1',
             'show_in_my_tickets': '1',
            },
            ]

MOCK_AREA = [{'id': u'test_id_1',
             'title': u'Internet',
             },
             {'id': u'test_id_2',
              'title': u'Intranet',
             },
             {'id': u'',
             'title': u'Test Id Area',
             },
            ]


MOCK_RELEASE = [{'id': u'version-1',
             'title': u'Version 1',
             },
             {'id': u'version-2',
              'title': u'Version 2',
             },
             {'id': u'',
             'title': u'Test Id Release',
             },
             ]


MOCK_PRIORITY = [{'id': u'test_id_1',
             'title': u'High',
             },
             {'id': u'test_id_2',
              'title': u'Low',
             },
             {'id': u'',
             'title': u'Test Id Priority',
             },
             ]


MOCK_RESPONSIBLE = [{'id': u'testuser',
             'title': u'Testuser',
             },
             {'id': u'admin',
              'title': u'Admin',
             },
             ]


class TicketBoxLayer(BasePTCLayer):
    """Layer for integration tests."""

    def afterSetUp(self):
        import Products.DataGridField
        zcml.load_config('configure.zcml', Products.DataGridField)
        ztc.installPackage('Products.DataGridField')

        import ftw.tabbedview
        zcml.load_config('configure.zcml', ftw.tabbedview)
        self.addProfile('ftw.tabbedview:default')

        import izug.ticketbox
        zcml.load_config('configure.zcml', izug.ticketbox)
        ztc.installPackage('izug.ticketbox')
        self.addProfile('izug.ticketbox:default')

ticketbox_integration_layer = TicketBoxLayer(bases=[ptc_layer])


class TicketBoxTestCase(ptc.PloneTestCase, unittest2.TestCase):

    layer = ticketbox_integration_layer

    def afterSetUp(self):
        # Set up sessioning objects
        ztc.utils.setupCoreSessions(self.app)

        self.workflow = getToolByName(self.portal, 'portal_workflow')
        self.acl_users = getToolByName(self.portal, 'acl_users')
        self.types = getToolByName(self.portal, 'portal_types')

        self.setRoles(('Manager',))

        #Create a Ticketbox on ploneroot
        self.portal.invokeFactory('Ticket Box', 'ticketbox')

        self.ticketbox = self.portal['ticketbox']
        self.ticketbox.getField('title').set(self.ticketbox, "Ticket Box Title")
        self.ticketbox.getField('description').set(self.ticketbox, "A TicketBox description")
        self.ticketbox.setIndividualIdentifier("ABC123")
        self.ticketbox.setAvailableStates(MOCK_STATE)
        self.ticketbox.setAvailableReleases(MOCK_RELEASE)
        self.ticketbox.setAvailableAreas(MOCK_AREA)
        self.ticketbox.setAvailablePriorities(MOCK_PRIORITY)

        #Generate Ids
        generate_datagrid_column_id(self.ticketbox, self)

        #Create a ticket on the ticketbox
        self.portal.ticketbox.invokeFactory('Ticket', 'ticket1')
        self.ticket1 = self.portal.ticketbox['ticket1']
        self.ticket1.getField('title').set(self.ticketbox, "Ticket Title")
        self.ticket1.getField('description').set(self.ticketbox, "A Ticket description")
        self.ticket1.getField('state').set(self.ticket1, MOCK_STATE[0]['id'])
        self.ticket1.getField('area').set(self.ticket1, MOCK_AREA[0]['id'])
        self.ticket1.getField('priority').set(self.ticket1, MOCK_PRIORITY[0]['id'])
        self.ticket1.getField('releases').set(self.ticket1, MOCK_RELEASE[0]['id'])
        self.ticket1.getField('responsibleManager').set(self.ticket1, "test_user_1_")
        self.ticket1.reindexObject()

        #Create a ticket on the ticketbox
        self.portal.ticketbox.invokeFactory('Ticket', 'ticket2')
        self.ticket2 = self.portal.ticketbox['ticket2']
        self.ticket2.getField('title').set(self.ticketbox, "Ticket Title")
        self.ticket2.getField('description').set(self.ticketbox, "A Ticket description")
        self.ticket2.getField('state').set(self.ticket2, MOCK_STATE[1]['id'])
        self.ticket2.getField('area').set(self.ticket2, MOCK_AREA[1]['id'])
        self.ticket2.getField('priority').set(self.ticket2, MOCK_PRIORITY[1]['id'])
        self.ticket2.getField('releases').set(self.ticket2, MOCK_RELEASE[1]['id'])
        self.ticket2.getField('responsibleManager').set(self.ticket2, "test_user_1_")
        self.ticket2.reindexObject()

        #Create responsecontainers
        self.container1 = ResponseContainer(self.ticket1)
        self.container2 = ResponseContainer(self.ticket2)

        #Create responses
        self.response1 = Response("response1")
        self.response2 = Response("response3")
        self.response3 = Response("response3")

class TicketboxFunctionalTestCase(ptc.FunctionalTestCase):
    """We use this class for functional integration tests that use doctest
    syntax. Again, we can put basic common utility or setup code in here.
    """
    layer = ticketbox_integration_layer

    def afterSetUp(self):
        # Set up sessioning objects
        ztc.utils.setupCoreSessions(self.app)

        self.workflow = getToolByName(self.portal, 'portal_workflow')
        self.acl_users = getToolByName(self.portal, 'acl_users')
        self.types = getToolByName(self.portal, 'portal_types')

        self.setRoles(('Manager',))

        #Create a Ticketbox on ploneroot
        self.portal.invokeFactory('Ticket Box', 'ticketbox')

        self.ticketbox = self.portal['ticketbox']
        self.ticketbox.getField('title').set(self.ticketbox, "Ticket Box Title")
        self.ticketbox.getField('description').set(self.ticketbox, "A TicketBox description")
        self.ticketbox.setIndividualIdentifier("ABC123")
        self.ticketbox.setAvailableStates(MOCK_STATE)
        self.ticketbox.setAvailableReleases(MOCK_RELEASE)
        self.ticketbox.setAvailableAreas(MOCK_AREA)
        self.ticketbox.setAvailablePriorities(MOCK_PRIORITY)
