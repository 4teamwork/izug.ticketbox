from ftw.tabbedview.browser.listing import CatalogListingView
from ftw.table import helper
from izug.ticketbox import ticketboxMessageFactory as _



class BaseTicketListingTab(CatalogListingView):
    """base tabbedview tab for listing tickets.
    """

    types = ['Ticket']

    show_selects = False

    sort_on = 'created'
    sort_reverse = True

    enabled_actions = major_actions = ['reset_tableconfiguration']

    def __init__(self, *args, **kwargs):
        super(BaseTicketListingTab, self).__init__(*args, **kwargs)

        self._state_map = None
        self._priority_map = None
        self._area_map = None

    @property
    def columns(self):
        return ({'column': 'getId',
                 'column_title': _(u"Id"),
                 'sort_index': 'sortable_id',
                 },

                {'column': 'Title',
                 'column_title': _(u"Description"),
                 'sort_index': 'sortable_title',
                 'transform': helper.linked_without_icon,
                 },

                {'column': 'getResponsibleManager',
                 'column_title': _(u"responsibleManager"),
                 'sort_index': 'sortable_responsibleManager',
                 'transform': helper.readable_author,
                 },

                {'column': 'getState',
                 'column_title': _(u"State"),
                 'transform': self.state_helper,
                 },

                {'column': 'getDueDate',
                 'column_title': _(u"DueDate"),
                 'transform': helper.readable_date_time_text,
                 },

                {'column': 'getPriority',
                 'column_title': _(u"Priority"),
                 'transform': self.priority_helper,
                 },

                {'column': 'getArea',
                 'column_title': _(u"Area"),
                 'transform': self.area_helper,
                 })

    def state_helper(self, item, stateid):
        if self._state_map is None:
            self._state_map = {}

            for state in self.context.getAvailableStates():
                self._state_map[state['id']] = state['title']

        return self._state_map.get(stateid, stateid)

    def priority_helper(self, item, priorityid):
        if self._priority_map is None:
            self._priority_map = {}

            for priority in self.context.getAvailablePriorities():
                self._priority_map[priority['id']] = priority['title']

        return self._priority_map.get(priorityid, priorityid)

    def area_helper(self, item, areaid):
        if self._area_map is None:
            self._area_map = {}

            for area in self.context.getAvailableAreas():
                self._area_map[area['id']] = area['title']

        return self._area_map.get(areaid, areaid)
