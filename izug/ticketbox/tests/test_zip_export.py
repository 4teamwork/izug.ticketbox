from datetime import datetime
from DateTime import DateTime
from ftw.builder import create, Builder
from ftw.testbrowser import browsing
from ftw.testing import freeze
from izug.ticketbox.testing import TICKETBOX_FUNCTIONAL_TESTING
from izug.ticketbox.tests import helpers
from StringIO import StringIO
from unittest2 import TestCase
from xlrd import open_workbook
from zipfile import ZipFile


class TestZipExport(TestCase):

    layer = TICKETBOX_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestZipExport, self).setUp()

        portal = self.layer['portal']
        helpers.login_as_manager(portal)

        self.ticketbox = create(Builder('ticket box').titled(u'Ticketbox'))

    @browsing
    def test_xls_in_zip_file(self, browser):
        ticket_builder = Builder('ticket')
        ticket_builder.titled(u'T\xc3st')
        ticket_builder.with_id('1')
        ticket_builder.having(dueDate=DateTime(2011, 11, 10, 17, 14, 35),
                              ticket_description='<p>This is a<br />test.</p>')
        ticket_builder.within(self.ticketbox)

        with freeze(datetime(2011, 2, 3, 5, 7, 11)):
            create(ticket_builder)

        browser.login()
        browser.visit(self.ticketbox, view='zip_export')
        self.assertEquals('application/zip', browser.headers['Content-Type'])

        zipfile = ZipFile(StringIO(browser.contents))
        self.assertEquals(['ticketbox.xlsx'], zipfile.namelist())

        xlsx = zipfile.read('ticketbox.xlsx')

        workbook = open_workbook(file_contents=xlsx)
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
                    u'Created': u'03.02.2011 05:07',
                    u'Due date': u'10.11.2011 17:14',
                    u'No.': u'1',
                    u'Description': u' This is a test. ',
                    u'Releases': u'',
                    u'Creator': u'test_user_1_',
                    u'Responsible': u'',
                    u'Watched release': u'',
                    u'Priorities': u'',
                    u'State': u'',
                    u'Variety': u'',
                    u'Title': u'T\xc3st',
                    u'Area': u'',
                }
            ],
            second=data
        )

    @browsing
    def test_ticket_attachment_in_zip_file(self, browser):
        ticket = create(Builder('ticket')
                        .titled(u'Ticket')
                        .within(self.ticketbox))

        file_ = StringIO('GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00'
                         '\x00\x00\x00!\xf9\x04\x04\x00\x00\x00\x00,\x00'
                         '\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
        file_.filename = 'im\xc3\xa4ge.gif'
        file_.content_type = 'image/gif'

        browser.login()
        browser.visit(ticket, view='edit')
        browser.fill({'attachment_file': file_}).submit()

        browser.visit(self.ticketbox, view='zip_export')
        zipfile = ZipFile(StringIO(browser.contents))
        image = zipfile.read(u'Ticket/image.gif')
        self.assertEqual(file_.getvalue(), image)
