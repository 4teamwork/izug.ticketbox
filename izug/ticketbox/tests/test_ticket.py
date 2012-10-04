import unittest
from izug.ticketbox.tests.base import TicketBoxTestCase
from DateTime import DateTime


class TestTicket(TicketBoxTestCase):

    def afterSetUp(self):
        super(TestTicket, self).afterSetUp()

    def beforeTearDown(self):
        pass

    def test_required_fields(self):
        title = self.ticket1.getField('title')
        description = self.ticket1.getField('description')

        self.assertEquals(title.required, True)
        self.assertEquals(description.required, False)

    def test_dates(self):
        due_date = self.ticket1.getField('dueDate').get(self.ticket1)
        answer_date = self.ticket1.getField('answerDate').get(self.ticket1)
        date = DateTime()+14

        self.assertEquals(due_date.Date(), date.Date())
        self.assertEquals(answer_date.Date(), date.Date())


def test_suite():
    """This sets up a test suite that actually runs the tests in the class
    above
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestTicket))
    return suite
