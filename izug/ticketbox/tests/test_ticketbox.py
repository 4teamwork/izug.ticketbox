import unittest
from izug.ticketbox.tests.base import TicketBoxTestCase


class TestTicketBox(TicketBoxTestCase):

    def afterSetUp(self):
        super(TestTicketBox, self).afterSetUp()

    def beforeTearDown(self):
        pass

    def test_required_fields(self):
        title = self.ticketbox.getField('title')
        description = self.ticketbox.getField('description')

        self.assertEquals(title.required, True)
        self.assertEquals(description.required, True)

    def test_generated_id(self):
        state = self.ticketbox.getAvailableStates()[2]['id']
        area = self.ticketbox.getAvailableAreas()[2]['id']
        release = self.ticketbox.getAvailableReleases()[2]['id']
        priority = self.ticketbox.getAvailablePriorities()[2]['id']

        self.assertEquals(state, "test-id-state")
        self.assertEquals(area, "test-id-area")
        self.assertEquals(release, "test-id-release")
        self.assertEquals(priority, "test-id-priority")




def test_suite():
    """This sets up a test suite that actually runs the tests in the class
    above
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestTicketBox))
    return suite
