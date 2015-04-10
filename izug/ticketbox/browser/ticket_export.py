# -*- coding: utf-8 -*-
from izug.ticketbox import export
from Products.Five.browser import BrowserView


class TicketsExport(BrowserView):
    """Returns a csv wincp52 ecoded file"""
    def __call__(self):
        response = self.request.RESPONSE
        filename = 'export_%s.csv' % self.context.getId()
        encoding = 'Windows-1252'
        csv = []

        # Header
        header = [field.encode('utf-8') for field
                  in export.get_header(self.context)]
        csv.append(','.join(header))

        # Data
        data = export.get_data(self.context)
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


class TicketsExportXlsx(TicketsExport):
    """Returns a XLSX file containing tickets."""

    def __call__(self, *args, **kwargs):
        response = self.request.RESPONSE

        header = export.get_header(self.context)
        data = export.get_data(self.context)
        excel_response = export.create_xlsx(header, data)

        filename = 'export_%s.xlsx' % self.context.getId()

        response.setHeader(
            'Content-Type',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response.setHeader(
            'Content-disposition',
            'attachment; filename={0}'.format(filename)
        )

        return excel_response.read()
