from izug.ticketbox.adapters import Response
from izug.ticketbox.interfaces import IResponseContainer
from izug.ticketbox.testing import TICKETBOX_INTEGRATION_TESTING
from izug.ticketbox.tests import helpers
from unittest2 import TestCase


class TestResponse(TestCase):

    layer = TICKETBOX_INTEGRATION_TESTING

    def setUp(self):
        super(TestResponse, self).setUp()

        portal = self.layer['portal']
        helpers.login_as_manager(portal)

        self.ticketbox = helpers.create_ticketbox(portal)
        self.ticket1 = helpers.create_ticket(self.ticketbox)
        self.ticket2 = helpers.create_ticket(self.ticketbox, data_index=1)

        self.container1 = IResponseContainer(self.ticket1)
        self.container2 = IResponseContainer(self.ticket2)

    def tearDown(self):
        helpers.remove_obj(self.ticketbox)
        helpers.logout_manager(self.layer['portal'])
        super(TestResponse, self).tearDown()

    def test_add_and_remove(self):
        response1 = Response('response1')
        response2 = Response('response3')
        response3 = Response('response3')

        self.assertEquals(len(self.container1), 0)
        self.assertEquals(len(self.container2), 0)

        self.container1.add(response1)
        self.container1.add(response2)
        self.container2.add(response3)

        self.assertEquals(len(self.container1), 2)
        self.assertEquals(len(self.container2), 1)

        self.container1.remove(0)
        self.container1.remove(1)

        self.assertEquals(response1 in self.container1, False)
        self.assertEquals(response2 in self.container1, False)
        self.assertEquals(response3 in self.container2, True)
