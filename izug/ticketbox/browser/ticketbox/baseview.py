from ftw.tabbedview.browser.listing import ListingView
from ftw.table import helper
from ftw.table.interfaces import ITableGenerator
from izug.ticketbox import ticketboxMessageFactory as _
from izug.ticketbox.browser.helper import map_attribute
from Products.CMFCore.utils import getToolByName
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import queryUtility
from ftw.table.basesource import BaseTableSource
from ftw.table.interfaces import ITableSourceConfig, ITableSource
from zope.interface import implements, Interface
from zope.component import adapts


class ITicketboxSourceConfig(ITableSourceConfig):
    """Marker interface for contact table source config.
    """


class TabbedTicketBoxBaseView(ListingView):
    implements(ITicketboxSourceConfig)

    filter_my_created_tickets = False
    filter_responsibleManager = False

    #str: show_in_my_tickets or show_in_all_tickets
    filter_state = None
    show_searchform = True
    sort_on = 'sortable_id'

    #template for the table generated from ftw.table
    table = ViewPageTemplateFile('table.pt')

    request_filters = [
            ('getResponsibleManager', 'responsible', None),
            ('getState', 'state', None),
            ('getReleases', 'release', None),
            ('getDueDate', 'duedate', None),
            ('getPriority', 'priority', None),
            ('getArea', 'area', None),
            ]

    def __init__(self, context, request):
        super(TabbedTicketBoxBaseView, self).__init__(context, request)
        self.columns = ({'column': 'getId',
                    'column_title': _(u"Id"),
                    'sort_index': 'sortable_id',
                    },
                    {'column': 'Title',
                    'column_title': _(u"Description"),
                    'sort_index': 'sortable_title',
                    'transform': self.izug_files_linked,
                    },
                    {'column': 'getResponsibleManager',
                    'column_title': _(u"responsibleManager"),
                    'sort_index': 'sortable_responsibleManager',
                    'transform': self.readable_author,
                    },
                    {'column': 'getState',
                    'column_title': _(u"State"),
                    'transform': self.map_state,
                    },
                    {'column': 'getDueDate',
                    'column_title': _(u"DueDate"),
                    'transform': helper.readable_date_time_text,
                    },
                    {'column': 'getPriority',
                    'column_title': _(u"Priority"),
                    'transform': self.map_priority,
                    },
                    {'column': 'getArea',
                    'column_title': _(u"Area"),
                    'transform': self.map_area,
                    },
                    )

    # HELPER Methods for ftw.table generator
    def map_state(self, item, id):
        """
        search the title-name of a list with the id
        """
        return map_attribute(self.context, "state", id)

    def map_priority(self, item, id):
        """
        search the title-name of a list with the id
        """
        return map_attribute(self.context, "priority", id)

    def map_area(self, item, id):
        """
        search the title-name of a list with the id
        """
        return map_attribute(self.context, "area", id)

    def get_attachment_ticket_nr(self, item, id):
        """
        get the ticketid from a attachment
        """
        url = item.getURL()
        split_url = url.split("/")

        #split_url should be at least 2
        if len(split_url) >= 2:
            ticket_url = "/".join(split_url[:-1])
            return "<a href='%s'># %s</a>" % (ticket_url, split_url[-2])
        else:
            return id

    def icon(self, item, value):
        """
        get MIME-Type icon
        """
        url_method = lambda: '#'
        #item = hasattr(item, 'aq_explicit') and item.aq_explicit or item
        if hasattr(item, 'getURL'):
            url_method = item.getURL
        elif hasattr(item, 'absolute_url'):
            url_method = item.absolute_url
        img = u'<img src="%s/%s"/>' % (item.portal_url(), item.getIcon)
        link = u'<a href="%s/at_download">%s</a>' % (url_method(), img)
        return link

    def izug_files_linked(self, item, value):
        """
        return a link to the item
        """
        url_method = lambda: '#'
        #item = hasattr(item, 'aq_explicit') and item.aq_explicit or item
        if hasattr(item, 'getURL'):
            url_method = item.getURL
        elif hasattr(item, 'absolute_url'):
            url_method = item.absolute_url
        value= value.decode('utf8')
        value = len(value) >= 47 and value[:47] + '...' or value

        extend_url = '/view'
        if item.portal_type == 'TicketAttachment':
            extend_url = '/at_download/file'

        link = u'<a href="%s%s">%s</a>' \
            % (url_method(), extend_url, value)
        return link

    def readable_author(self, item, author):
        """
        get the full name by user-id
        """
        if not author:
            return '-'
        name = author
        user = item.acl_users.getUserById(author)
        if user is None:
            return _(u"unassigned")
        else:
            name = user.getProperty('fullname', author)
            if not len(name):
                name = author
            return name


    def get_base_query(self):
        """Returns the base query for a specific table source type
        (e.g. portal_catalog, sqlalchemy, dict, ...).
        """
        query = {}

        # extend with path filter, if configured
        if 'path' not in query and getattr(self, 'filter_path', None):
            query['path'] = {'query': self.filter_path,
                             'depth': self.depth}

        # extend with types
        if 'types' not in query and self.types:
            query['portal_type'] = self.types

        return query

    def render_listing(self):

        generator = queryUtility(ITableGenerator, 'ftw.tablegenerator')
        return generator.generate(self.batch,
                                  self.columns,
                                  sortable=True,
                                  selected=(self.sort_on, self.sort_order),
                                  template=self.table,
                                  css_mapping=dict(table='sortable-table'),
                                  )



class TabbedTicketboxtableSource(BaseTableSource):
    implements(ITableSource)
    adapts(ITicketboxSourceConfig, Interface)


    def search_results(self, query):

        """Custom search method for ticketbox"""
        membership = self.config.context.aq_inner.portal_membership
        member_id = membership.getAuthenticatedMember().getId()

        # Huck for overview tab.
        # Should return nothing if no filter criteria is present.
        view_name = self.request.get('view_name')
        if view_name == "Overview":

            is_set_responsible = self.config.request.get('responsible')
            is_set_state = self.config.request.get('state')
            is_set_release = self.config.request.get('release')
            is_set_area = self.config.request.get('area')
            is_set_priority = self.config.request.get('priority')

            if is_set_responsible:
                query['getResponsibleManager'] = is_set_responsible
            elif is_set_state:
                query['getState'] = is_set_state
            elif is_set_release:
                query['getReleases'] = is_set_release
            elif is_set_priority:
                query['getPriority'] = is_set_priority
            elif is_set_area:
                query['getArea'] = is_set_area

            if not (is_set_responsible or
                    is_set_state or
                    is_set_release or
                    is_set_area or
                    is_set_priority):

                return []
        # show only tickets, where creater is me
        if self.config.filter_my_created_tickets:
            query['Creator'] = member_id

        # show only tickets, where ResponsibleManager is me
        if self.config.filter_responsibleManager:
            query['getResponsibleManager'] = member_id
        self.config.catalog = catalog = getToolByName(self.config.context, 'portal_catalog')
        tmpresults = catalog(**query)
        # Filter by state (ATField State not review_state)
        if not self.config.filter_state:
            return tmpresults
        else:
            states = self.config.context.getAvailableStates()
            state_mapping = {}
            for item in states:
                state_mapping[item['id']] = item[self.config.filter_state]
            result = []
            for item in tmpresults:
                if state_mapping[item.getState] == '1':
                    result.append(item)

            return result

    def extend_query_with_textfilter(self, results, text):
        return results

    def extend_query_with_ordering(self, results):
        return results

