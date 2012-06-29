from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from copy import deepcopy
from izug.ticketbox import ticketboxMessageFactory as _
from izug.ticketbox.browser.tabbed.base import BaseTicketListingTab


def collect_filter_information(items, filters):
    """Creates a dict of filter information from items (brains) and a filter
    configuration.

    filters example:

    >>> filters = {
    ...     'getResponsibleManager': {
    ...         'options': [{'id': 'john.doe', 'title': 'John Doe'}],
    ...         'label': _(u'getResponsibleManager')},
    ... }

    """

    filters = deepcopy(filters)

    # cleanup options to general format
    for filterid, filter in filters.items():
        options = []
        for option in filters[filterid]['options']:

            if isinstance(option, dict):
                options.append(deepcopy(option))

            else:
                options.append({'id': option[0],
                                'title': option[1],
                                'original': option})

        filters[filterid]['options'] = options

    # count matches of every option
    filter_options = {}
    for filterid, filter in filters.items():
        filter_options[filterid] = {}
        for option in filter.get('options', []):
            filter_options[filterid][option['id']] = 0

    for item in items:
        for key in filter_options.keys():
            value = getattr(item, key, None)
            if value and value in filter_options[key]:
                filter_options[key][value] += 1

    # update info with matches
    for filterid, options in filter_options.items():
        filters[filterid]['filterid'] = filterid
        for option in filters[filterid]['options']:
            option['matches'] = options[option['id']]

    return filters


class OverviewTab(BaseTicketListingTab):
    """Ticket overview
    """

    template = ViewPageTemplateFile('overview.pt')

    def get_base_query(self):
        filterid = self.request.get('filterid', None)

        if not filterid:
            # Do not display any results when no filter is selected.
            self.depth = 0

        query = super(OverviewTab, self).get_base_query()

        if filterid:
            filtervalue = self.request.get('filtervalue', None)
            query[filterid] = filtervalue

        return query

    def get_filter_info(self):
        """Returns a list of columns containing filters with all necessary data
        for rendering in the template.
        """

        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog({'portal_type': ['Ticket'],
                          'path': '/'.join(self.context.getPhysicalPath())})

        filter_data = collect_filter_information(
            brains, self._get_filter_configuration())

        return (
            # column 1
            [filter_data['getResponsibleManager']],

            # column 2
            [filter_data['getState'],
             filter_data['getVariety']],

            # column 3
            [filter_data['getReleases'],
             filter_data['getWatchedRelease']],

            # column 4
            [filter_data['getPriority'],
             filter_data['getArea']])

    def _get_filter_configuration(self):
        filters = {}
        filters['getResponsibleManager'] = {
            'label': _(u'label_heading_by_responsible',
                       default=u'By responsible'),
            'options': sorted(
                self.context.assignable_users(),
                key=lambda item: item[1].lower().decode('utf-8'))}

        filters['getState'] = {
            'label': _(u'label_heading_by_states'),
            'options': self.context.getAvailableStates()}

        available_releases = self.context.getAvailableReleases()
        filters['getReleases'] = {
            'label': _(u'label_heading_by_release'),
            'options': available_releases}

        filters['getWatchedRelease'] = {
            'label': _(u'label_heading_by_watched_release'),
            'options': available_releases}

        filters['getPriority'] = {
            'label': _(u'label_heading_by_severities'),
            'options': self.context.getAvailablePriorities()}

        filters['getArea'] = {
            'label': _(u'label_heading_by_area'),
            'options': self.context.getAvailableAreas()}

        filters['getVariety'] = {
            'label': _(u'label_heading_by_varieties'),
            'options': self.context.getAvailableVarieties()}

        return filters
