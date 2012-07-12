import unittest
from izug.ticketbox.tests.base import TicketBoxTestCase


class TestResponse(TicketBoxTestCase):

    def afterSetUp(self):
        super(TestResponse, self).afterSetUp()

    def beforeTearDown(self):
        pass

    def test_add_and_remove(self):

        self.assertEquals(len(self.container1), 0)
        self.assertEquals(len(self.container2), 0)

        self.container1.add(self.response1)
        self.container1.add(self.response2)
        self.container2.add(self.response3)

        self.assertEquals(len(self.container1), 2)
        self.assertEquals(len(self.container2), 1)

        self.container1.remove(0)
        self.container1.remove(1)

        self.assertEquals(self.response1 in self.container1, False)
        self.assertEquals(self.response2 in self.container1, False)
        self.assertEquals(self.response3 in self.container2, True)


def test_suite():
    """This sets up a test suite that actually runs the tests in the class
    above
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestResponse))
    return suite
