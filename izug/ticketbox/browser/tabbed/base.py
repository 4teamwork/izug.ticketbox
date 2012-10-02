from ftw.tabbedview.browser.listing import CatalogListingView
from ftw.table import helper
from izug.ticketbox import ticketboxMessageFactory as _
from zope.i18n import translate


class BaseTicketListingTab(CatalogListingView):
    """base tabbedview tab for listing tickets.
    """

    types = ['Ticket']

    show_selects = False
    show_menu = False

    sort_on = 'created'
    sort_reverse = True

    def __init__(self, *args, **kwargs):
        super(BaseTicketListingTab, self).__init__(*args, **kwargs)

        self._cached_ticketbox_options = None
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
                 'transform': self.readable_author_helper,
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

    def readable_author_helper(self, item, userid):
        if userid == '(UNASSIGNED)':
            return translate(_(u'None'), context=self.request)

        else:
            return helper.readable_author(item, userid)

    def _get_ticketbox_path_for(self, item):
        """Returns the ticketbox path for an item.
        """
        return '/'.join(self.context.getPhysicalPath())

    def _get_cached_options_for(self, item, getter_name):
        """Returns all available options for the field with the
        getter name `getter_name` of the ticket box of the
        current item.
        """

        if self._cached_ticketbox_options is None:
            self._cached_ticketbox_options = {}

        box_path = self._get_ticketbox_path_for(item)
        if box_path not in self._cached_ticketbox_options:
            self._cached_ticketbox_options[box_path] = {}
        box_cache = self._cached_ticketbox_options[box_path]

        if getter_name not in box_cache:
            box_cache[getter_name] = {}

            box = self.context.restrictedTraverse(box_path)
            for option in getattr(box, getter_name)():
                box_cache[getter_name][option['id']] = option['title']

        return box_cache[getter_name]

    def state_helper(self, item, stateid):
        options = self._get_cached_options_for(item, 'getAvailableStates')
        return options.get(stateid)

    def priority_helper(self, item, priorityid):
        options = self._get_cached_options_for(item, 'getAvailablePriorities')
        return options.get(priorityid)

    def area_helper(self, item, areaid):
        options = self._get_cached_options_for(item, 'getAvailableAreas')
        return options.get(areaid)
