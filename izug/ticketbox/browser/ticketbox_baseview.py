from Products.CMFCore.utils import getToolByName
from izug.arbeitsraum.browser.views import MyListing
from izug.ticketbox import ticketboxMessageFactory as _
from ftw.table import helper
from izug.arbeitsraum.browser.views import izug_files_linked


def readable_author(item, author):
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

class TabbedTicketBoxBaseView(MyListing):

    filter_my_tickets = False
    filter_state = None

    request_filters = [
        ('responsibleManager', 'responsible', None),
        ('State', 'state', None),
        ('Releases', 'release', None),
        ('Area', 'area', None),
        ('Priority', 'priority', None),
        ]


    def __init__(self, context, request):
        super(TabbedTicketBoxBaseView, self).__init__(context, request)

        self.columns = ({'column':'getId',
                        'column_title':_(u"Id"),
                        },
                        {'column':'Title',
                        'column_title':_(u"Title"),
                        'sort_index': 'sortable_title',
                        'transform':izug_files_linked,
                        },
                        {'column':'responsibleManager',
                        'column_title':_(u"responsibleManager"),
                        'transform':readable_author,
                        },
                        {'column':'State',
                        'column_title':_(u"State"),
                        'transform':self.map_state,
                        },
                        {'column':'Due_date',
                        'column_title':_(u"Due_Date"),
                        'transform':helper.readable_date_time_text,
                        },
                        {'column':'Priority',
                        'column_title':_(u"Priority"),
                        'transform':self.map_priority,
                        },
                        {'column':'Area',
                        'column_title':_(u"Area"),
                        'transform':self.map_area,
                        },
                        )


    def search(self, kwargs):

        """Custom search method for ticketbox"""

        # show only my_tickets
        if self.filter_my_tickets:
            kwargs['responsibleManager'] = \
                self.context.aq_inner.portal_membership.getAuthenticatedMember().getId()
        self.catalog = catalog = getToolByName(self.context,'portal_catalog')
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
                if state_mapping[item.State] == '1':
                    result.append(item)
            self.contents = result


        self.len_results = len(self.contents)


    # HELPER Methods for ftw.table generator
    def map_state(self, item, id):
        """
        search the title-name of a list with the id
        """
        states = self.context.getAvailableStates()
        for state in states:
            if id == state['id']:
                return state['title']

    def map_priority(self, item, id):
        """
        search the title-name of a list with the id
        """
        priorities = self.context.getAvailablePriorities()

        for priority in priorities:
            if id == priority['id']:
                return priority['title']

    def map_area(self, item, id):
        """
        search the title-name of a list with the id
        """
        areas = self.context.getAvailableAreas()

        for area in areas:
            if id == area['id']:
                return area['title']