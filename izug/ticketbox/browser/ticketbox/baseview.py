from ftw.tabbedview.browser.views.views import BaseListingView
from ftw.table import helper
from ftw.table.interfaces import ITableGenerator
from izug.ticketbox import ticketboxMessageFactory as _
from izug.ticketbox.browser.helper import map_attribute
from Products.CMFCore.utils import getToolByName
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import queryUtility


class TabbedTicketBoxBaseView(BaseListingView):

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

    def update(self):
        super(TabbedTicketBoxBaseView, self).update()
        self.pagesize = 50
        #old izug batching still uses b_start instead of self.pagenumber
        self.pagenumber = int(self.request.get('b_start', 0))/self.pagesize+1

    def render_listing(self):

        generator = queryUtility(ITableGenerator, 'ftw.tablegenerator')
        return generator.generate(self.batch,
                                  self.columns,
                                  sortable=True,
                                  selected=(self.sort_on, self.sort_order),
                                  template=self.table,
                                  auto_count=self.auto_count,
                                  css_mapping=dict(table='sortable-table'),
                                  )

    def search(self, kwargs):

        """Custom search method for ticketbox"""
        membership = self.context.aq_inner.portal_membership
        member_id = membership.getAuthenticatedMember().getId()

        # Huck for overview tab.
        # Should return nothing if no filter criteria is present.
        view_name = self.request.get('view_name')
        if view_name == "Overview":

            is_set_responsible = self.request.get('responsible')
            is_set_state = self.request.get('state')
            is_set_release = self.request.get('release')
            is_set_area = self.request.get('area')
            is_set_priority = self.request.get('priority')

            if not (is_set_responsible or
                    is_set_state or
                    is_set_release or
                    is_set_area or
                    is_set_priority):

                self.contents = []
                self.len_results = 0
                return

        # show only tickets, where creater is me
        if self.filter_my_created_tickets:
            kwargs['Creator'] = member_id

        # show only tickets, where ResponsibleManager is me
        if self.filter_responsibleManager:
            kwargs['responsibleManager'] = member_id

        self.catalog = catalog = getToolByName(self.context, 'portal_catalog')
        query = self.build_query(**kwargs)
        tmpresults = catalog(**query)

        # Filter by state (ATField State not review_state)
        if not self.filter_state:
            self.contents = tmpresults
        else:
            states = self.context.getAvailableStates()
            state_mapping = {}
            for item in states:
                state_mapping[item['id']] = item[self.filter_state]
            result = []
            for item in tmpresults:
                if state_mapping[item.getState] == '1':
                    result.append(item)

            self.contents = result

        self.len_results = len(self.contents)



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
        value = len(value) >= 47 and value[:47] + '...' or value

        extend_url = '/view'
        if item.portal_type == 'TicketAttachment':
            extend_url = '/at_download/file'

        link = u'<a class="testclass" href="%s%s" title=%s>%s</a>' \
            % (url_method(), extend_url, item.Description, value.decode('utf8'))
        return link

    def readable_author(self, item, author):
        """
        get the full name of a user-id
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
