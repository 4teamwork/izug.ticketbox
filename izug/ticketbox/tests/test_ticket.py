from DateTime import DateTime
from izug.ticketbox.testing import TICKETBOX_INTEGRATION_TESTING
from izug.ticketbox.tests import helpers
from unittest2 import TestCase


class TestTicket(TestCase):

    layer = TICKETBOX_INTEGRATION_TESTING

    def setUp(self):
        super(TestTicket, self).setUp()

        portal = self.layer['portal']

        helpers.login_as_manager(portal)
        self.ticketbox = helpers.create_ticketbox(portal)
        self.ticket = helpers.create_ticket(self.ticketbox)

    def tearDown(self):
        helpers.remove_obj(self.ticketbox)
        helpers.logout_manager(self.layer['portal'])
        super(TestTicket, self).tearDown()

    def test_required_fields(self):
        title = self.ticket.getField('title')
        description = self.ticket.getField('description')

        self.assertEquals(title.required, True)
        self.assertEquals(description.required, False)

    def test_dates(self):
        due_date = self.ticket.getField('dueDate').get(self.ticket)
        answer_date = self.ticket.getField('answerDate').get(self.ticket)
        date = DateTime() + 14

        self.assertEquals(due_date.Date(), date.Date())
        self.assertEquals(answer_date.Date(), date.Date())
