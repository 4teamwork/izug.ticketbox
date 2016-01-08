from DateTime import DateTime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from izug.ticketbox.adapters import Response
from izug.ticketbox.interfaces import IResponseContainer
from izug.ticketbox.testing import TICKETBOX_FUNCTIONAL_TESTING
from izug.ticketbox.tests import helpers
from unittest2 import TestCase


class TestResponse(TestCase):

    layer = TICKETBOX_FUNCTIONAL_TESTING

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

    @browsing
    def test_update_anserdate_if_given(self, browser):
        ticketbox = create(Builder('ticket box'))
        ticket = create(Builder('ticket')
                        .having(answerDate=DateTime(2015, 12, 31))
                        .within(ticketbox))

        browser.login().visit(ticket)

        browser.fill({
            'answerdate_year': '2021',
            'answerdate_month': 'April',
            'answerdate_day': '12',
            'answerdate_hour': '10',
            'answerdate_minute': '05'}).submit()

        self.assertEqual(
            1, len(browser.css('.response-reply')),
            "There should be one response visible")

        self.assertEqual(
            ['31.12.2015 00:00', '12.04.2021 10:05'],
            browser.css('.response-reply .issueChange').text,
            "The answerdate before and the answerdatedate after should "
            "be visible in the answer")

    @browsing
    def test_do_not_update_anserdate_if_no_new_date_is_given(self, browser):
        ticketbox = create(Builder('ticket box'))
        ticket = create(Builder('ticket')
                        .having(answerDate=DateTime(2015, 12, 31, 9, 50))
                        .within(ticketbox))

        browser.login().visit(ticket)

        browser.fill({
            'answerdate_year': '2015',
            'answerdate_month': 'December',
            'answerdate_day': '31',
            'answerdate_hour': '09',
            'answerdate_minute': '50'}).submit()

        self.assertEqual(
            ['No response text added and no issue changes made.'],
            statusmessages.error_messages())

    @browsing
    def test_do_not_update_anserdate_if_no_year_is_given(self, browser):
        ticketbox = create(Builder('ticket box'))
        ticket = create(Builder('ticket')
                        .having(answerDate=DateTime(2015, 12, 31))
                        .within(ticketbox))

        browser.login().visit(ticket)

        browser.fill({
            'answerdate_year': '--',
            'answerdate_month': 'April',
            'answerdate_day': '04',
            'answerdate_hour': '09',
            'answerdate_minute': '00'}).submit()

        self.assertEqual(
            ['No response text added and no issue changes made.'],
            statusmessages.error_messages())

    @browsing
    def test_do_not_update_anserdate_if_no_month_is_given(self, browser):
        ticketbox = create(Builder('ticket box'))
        ticket = create(Builder('ticket')
                        .having(answerDate=DateTime(2015, 12, 31))
                        .within(ticketbox))

        browser.login().visit(ticket)

        browser.fill({
            'answerdate_year': '2021',
            'answerdate_month': '--',
            'answerdate_day': '04',
            'answerdate_hour': '09',
            'answerdate_minute': '00'}).submit()

        self.assertEqual(
            ['No response text added and no issue changes made.'],
            statusmessages.error_messages())

    @browsing
    def test_do_not_update_anserdate_if_no_day_is_given(self, browser):
        ticketbox = create(Builder('ticket box'))
        ticket = create(Builder('ticket')
                        .having(answerDate=DateTime(2015, 12, 31))
                        .within(ticketbox))

        browser.login().visit(ticket)

        browser.fill({
            'answerdate_year': '2021',
            'answerdate_month': 'April',
            'answerdate_day': '--',
            'answerdate_hour': '09',
            'answerdate_minute': '00'}).submit()

        self.assertEqual(
            ['No response text added and no issue changes made.'],
            statusmessages.error_messages())

    @browsing
    def test_update_anserdate_if_no_hour_or_minute_is_given(self, browser):
        ticketbox = create(Builder('ticket box'))
        ticket = create(Builder('ticket')
                        .having(answerDate=DateTime(2015, 12, 31))
                        .within(ticketbox))

        browser.login().visit(ticket)

        browser.fill({
            'answerdate_year': '2021',
            'answerdate_month': 'April',
            'answerdate_day': '12',
            'answerdate_hour': '--',
            'answerdate_minute': '--'}).submit()

        self.assertEqual(
            1, len(browser.css('.response-reply')),
            "There should be one response visible")
