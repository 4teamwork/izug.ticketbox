# -*- coding: utf-8 -*-
import StringIO

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
import xlsxwriter

from izug.ticketbox import ticketboxMessageFactory as _


def format_date(date):
    if not date:
        return ''
    if date.year() <= 1900:
        return ''
    else:
        return date.strftime('%d.%m.%Y %H:%M')


def map_base(available_items, id_):
    """Basemapping for attributes in ticketbox
    """

    for available_item in available_items:
        if id_ == available_item.get('id'):
            return available_item.get('title')
    return "-"


class TicketsExport(BrowserView):
    """Returns a csv wincp52 ecoded file"""

    def fullname(self, uid):
        member = self.context.portal_membership.getMemberById(uid)
        if member:
            fullname = member.getProperty('fullname', member.getId())
            if fullname:
                return fullname
            return member.getId()
        return uid

    def __call__(self):
        response = self.request.RESPONSE
        filename = 'export_%s.csv' % self.context.getId()
        encoding = 'Windows-1252'
        csv = []

        # Header
        header = [field.encode('utf-8') for field in self.get_header()]
        csv.append(','.join(header))

        # Data
        data = self.get_data()
        for row in data:
            # Change double quote to single
            row = [val.replace('"', "'") for val in row]

            # Put every value in double quote
            row = ['"%s"' % val for val in row]
            csv.append(','.join(row))

        result = '\n'.join(csv).decode('utf-8').encode(encoding, 'replace')

        response.setHeader('Content-Type',
                           'text/csv; charset=%s' % encoding)
        response.setHeader(
            'Content-disposition',
            'attachment; filename={0}'.format(filename))

        return result

    def get_header(self):
        return [
            self.context.translate(
                _(u'csv_heading_nr', default=u'Nr.')),
            self.context.translate(
                _(u'csv_heading_title', default=u'Title')),
            self.context.translate(
                _(u'csv_heading_description', default=u'Description')),
            self.context.translate(
                _(u'csv_heading_creator', default=u'Creator')),
            self.context.translate(
                _(u'csv_heading_created', default=u'Created')),
            self.context.translate(
                _(u'csv_heading_responsible', default=u'Responsible')),
            self.context.translate(
                _(u'csv_heading_state', default=u'State')),
            self.context.translate(
                _(u'csv_heading_priorities', default=u'Priorities')),
            self.context.translate(
                _(u'csv_heading_area', default=u'Area')),
            self.context.translate(
                _(u'csv_heading_variety', default=u'Variety')),
            self.context.translate(
                _(u'csv_heading_releases', default=u'Releases')),
            self.context.translate(
                _(u'csv_heading_watched_release', default=u'Watched release')),
            self.context.translate(
                _(u'csv_heading_watched_duedate', default=u'Duedate')),
        ]

    def get_data(self):
        data = []
        brains = list(self.context.portal_catalog(
            {
                'portal_type': 'Ticket',
                'sort_on': 'getId',
                'path': {
                    'query': '/'.join(self.context.getPhysicalPath()),
                    'depth': 2,
                }
            }
        ))

        pt = getToolByName(self.context, 'portal_transforms')
        for brain in brains:
            row = [
                brain.getId,
                brain.Title,
                pt.convertTo('text/plain', brain.Description).getData(),
                self.fullname(brain.Creator),
                format_date(brain.created),
                self.fullname(brain.getResponsibleManager),
                map_base(
                    self.context.getAvailableStates(),
                    brain.getState
                ),
                map_base(
                    self.context.getAvailablePriorities(),
                    brain.getPriority
                ),
                map_base(
                    self.context.getAvailableAreas(),
                    brain.getArea)
                ,
                map_base(
                    self.context.getAvailableVarieties(),
                    brain.getVariety
                ),
                map_base(
                    self.context.getAvailableReleases(),
                    brain.getReleases
                ),
                map_base(
                    self.context.getAvailableReleases(),
                    brain.getWatchedRelease
                ),
                format_date(brain.getDueDate)
            ]
            data.append(row)

        return data


class TicketsExportXlsx(TicketsExport):
    """Returns a XLSX file containing tickets."""

    def __call__(self, *args, **kwargs):
        response = self.request.RESPONSE

        header = self.get_header()
        data = self.get_data()
        excel_response = self.create_xlsx(header, data)

        filename = 'export_%s.xlsx' % self.context.getId()

        response.setHeader(
            'Content-Type',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response.setHeader(
            'Content-disposition',
            'attachment; filename={0}'.format(filename)
        )

        return excel_response

    def create_xlsx(self, header=None, data=None):
        if not header:
            header = []
        if not data:
            data = []

        # Create an in-memory output file for the new workbook.
        output = StringIO.StringIO()

        # Even though the final file will be in memory the module uses temp
        # files during assembly for efficiency. To avoid this on servers that
        # don't allow temp files, for example the Google APP Engine, set the
        # 'in_memory' constructor option to True.
        workbook = xlsxwriter.Workbook(output, {'in_memory': False})
        worksheet = workbook.add_worksheet()

        # Add a bold format for the header.
        bold = workbook.add_format({'bold': True})

        # Write the header.
        for index, item in enumerate(header):
            worksheet.write(0, index, item, bold)

        # Write the data (which is a nested list).
        for row_index, row_item in enumerate(data):
            for column_index, column_item in enumerate(row_item):
                worksheet.write_string(
                    row_index+1, column_index, column_item.decode('utf-8'))

        # Set the auto filter only if there is something to filter.
        if header and data:
            worksheet.autofilter(0, 0, len(data)+1, len(data[0])-1)

        workbook.close()

        # Rewind the buffer.
        output.seek(0)

        return output.read()
