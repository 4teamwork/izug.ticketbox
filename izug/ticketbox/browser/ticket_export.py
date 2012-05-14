from Products.Five.browser import BrowserView
from izug.ticketbox import ticketboxMessageFactory as _


def format_date(date):
    if not date:
        return ''
    if date.year() <= 1900:
        return ''
    else:
        return date.strftime('%d.%m.%Y %H:%m')


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
        context = self.context
        filename = 'export_%s.csv' % self.context.getId()
        encoding = 'Windows-1252'
        csv = []

        brains = list(context.portal_catalog({
            'portal_type': 'Ticket',
            'sort_on': 'getId',
            'path': {
                'query': '/'.join(context.getPhysicalPath()), 'depth': 2}}))

        headers = [
            context.translate(_(u'csv_heading_nr', default=u'Nr.')),
            context.translate(_(u'csv_heading_title', default=u'Title')),
            context.translate(
                _(u'csv_heading_description', default=u'Description')),
            context.translate(_(u'csv_heading_creator', default=u'Creator')),
            context.translate(_(u'csv_heading_created', default=u'Created')),
            context.translate(
                _(u'csv_heading_responsible', default=u'Responsible')),
            context.translate(_(u'csv_heading_state', default=u'State')),
            context.translate(
                _(u'csv_heading_priorities', default=u'Priorities')),
            context.translate(_(u'csv_heading_area', default=u'Area')),
            context.translate(_(u'csv_heading_variety', default=u'Variety')),
            context.translate(_(u'csv_heading_releases', default=u'Releases')),
            context.translate(
                _(u'csv_heading_watched_release', default=u'Watched release')),
            context.translate(
                _(u'csv_heading_watched_duedate', default=u'Duedate')),
            ]

        # Header
        csv.append(','.join(
            [field.encode('utf-8') for field in headers]))

        # Data
        for brain in brains:
            row = []
            row.append(brain.getId)
            row.append(brain.Title)
            row.append(brain.Description)
            row.append(self.fullname(brain.Creator))
            row.append(format_date(brain.created))
            row.append(self.fullname(brain.getResponsibleManager))
            row.append(map_base(
                context.getAvailableStates(), brain.getState))
            row.append(map_base(
                context.getAvailablePriorities(), brain.getPriority))
            row.append(map_base(
                context.getAvailableAreas(), brain.getArea))
            row.append(map_base(
                context.getAvailableVarieties(), brain.getVariety))
            row.append(map_base(
                context.getAvailableReleases(), brain.getReleases))
            row.append(map_base(
                context.getAvailableReleases(), brain.getWatchedRelease))
            row.append(format_date(brain.getDueDate))

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
            'attachment; %s; filename=%s' % (encoding, filename))
        return result
