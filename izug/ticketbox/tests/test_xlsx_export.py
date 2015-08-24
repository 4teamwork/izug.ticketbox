# * coding: utf8 *
from datetime import datetime
from DateTime import DateTime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testing import freeze
from izug.ticketbox.testing import TICKETBOX_INTEGRATION_TESTING
from izug.ticketbox.tests import helpers
from unittest2 import TestCase
from xlrd import open_workbook


class TestXlsxExport(TestCase):

    layer = TICKETBOX_INTEGRATION_TESTING

    def setUp(self):
        super(TestXlsxExport, self).setUp()

        portal = self.layer['portal']
        helpers.login_as_manager(portal)

    def test_xlsx_export(self):
        ticketbox = create(Builder('ticket box')
                           .titled(u'My Tickät Box'))

        ticket_builder = Builder('ticket')
        ticket_builder.titled(u'Täst')
        ticket_builder.with_id('1')
        ticket_builder.having(dueDate=DateTime(2010, 11, 10, 17, 14, 35),
                              ticket_description="<p>This is a<br />test.</p>")
        ticket_builder.within(ticketbox)

        with freeze(datetime(2010, 11, 1, 8, 25, 20)):
            create(ticket_builder)

        export_view = ticketbox.restrictedTraverse('tickets_export_xlsx')
        response = export_view()

        workbook = open_workbook(file_contents=response)
        sheet = workbook.sheet_by_index(0)

        data = map(sheet.row_values, range(sheet.nrows))
        headers = data.pop(0)
        data = map(
            lambda row: dict(zip(headers, row)),
            data
        )
        self.maxDiff = None
        self.assertEquals(
            first=[
                {
                    u'Created': u'01.11.2010 08:25',
                    u'Due date': u'10.11.2010 17:14',
                    u'No.': u'1',
                    u'Description': u' This is a test. ',
                    u'Releases': u'',
                    u'Creator': u'test_user_1_',
                    u'Responsible': u'',
                    u'Watched release': u'',
                    u'Priorities': u'',
                    u'State': u'',
                    u'Variety': u'',
                    u'Title': u'Täst',
                    u'Area': u'',
                }
            ],
            second=data
        )
