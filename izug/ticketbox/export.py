from browser.helper import map_base
from izug.ticketbox import ticketboxMessageFactory as _
from Products.CMFCore.utils import getToolByName
import StringIO
import xlsxwriter
from zope.i18n import translate


def format_date(date):
    if not date:
        return ''
    if date.year() <= 1900:
        return ''
    else:
        return date.strftime('%d.%m.%Y %H:%M')


def fullname(context, uid):
    member = context.portal_membership.getMemberById(uid)
    if member:
        fullname = member.getProperty('fullname', member.getId())
        if fullname:
            return fullname
        return member.getId()
    return uid


def get_header(context):
    return [
        context.translate(
            _(u'export_heading_nr', default=u'No.')),
        context.translate(
            _(u'export_heading_title', default=u'Title')),
        context.translate(
            _(u'export_heading_description', default=u'Description')),
        context.translate(
            _(u'export_heading_creator', default=u'Creator')),
        context.translate(
            _(u'export_heading_created', default=u'Created')),
        context.translate(
            _(u'export_heading_responsible', default=u'Responsible')),
        context.translate(
            _(u'export_heading_state', default=u'State')),
        context.translate(
            _(u'export_heading_priorities', default=u'Priorities')),
        context.translate(
            _(u'export_heading_area', default=u'Area')),
        context.translate(
            _(u'export_heading_variety', default=u'Variety')),
        context.translate(
            _(u'export_heading_releases', default=u'Releases')),
        context.translate(
            _(u'export_heading_watched_release', default=u'Watched release')),
        context.translate(
            _(u'export_heading_watched_due_date', default=u'Due date')),
    ]


def get_data(context):
    data = []
    brains = list(context.portal_catalog(
        {
            'portal_type': 'Ticket',
            'sort_on': 'getId',
            'path': {
                'query': '/'.join(context.getPhysicalPath()),
                'depth': 2,
            }
        }
    ))

    pt = getToolByName(context, 'portal_transforms')
    for brain in brains:
        obj = brain.getObject()
        ticket_description = obj.getTicket_description()
        row = [
            brain.getId,
            brain.Title,
            pt.convertTo('text/plain', ticket_description).getData(),
            fullname(context, brain.Creator),
            format_date(brain.created),
            fullname(context, brain.getResponsibleManager),
            map_base(
                context.getAvailableStates(),
                brain.getState),
            map_base(
                context.getAvailablePriorities(),
                brain.getPriority),
            map_base(
                context.getAvailableAreas(),
                brain.getArea),
            map_base(
                context.getAvailableVarieties(),
                brain.getVariety),
            map_base(
                context.getAvailableReleases(),
                brain.getReleases),
            map_base(
                context.getAvailableReleases(),
                brain.getWatchedRelease),
            format_date(brain.getDueDate)
        ]
        data.append(row)

    return data


def create_xlsx(header=None, data=None):
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

    return output
