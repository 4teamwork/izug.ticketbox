from izug.ticketbox.browser.ticketbox.baseview import TabbedTicketBoxBaseView
from Products.CMFCore.utils import getToolByName
from izug.ticketbox import ticketboxMessageFactory as _
from plone.memoize import ram


@ram.cache(lambda m, i, author: ("readable_author", author))
def readable_author(item, author):
    #TODO: terribly inefficient. Make some HelperCommons or something
    if not author:
        return '-'
    name = author
    user = item.acl_users.getUserById(author)
    if user is not None:
        name = user.getProperty('fullname', author) or author
        if not len(name):
            name = author
    return '<a href="%s/author/%s">%s</a>' % (item.portal_url(), author, name)


class TabbedTicketBoxOverviewBaseView(TabbedTicketBoxBaseView):
    """ Baseview for tabs in the ticketbox overview view
    """

    def map_state(self, item, id):
        """
        search the title-name of a list with the id
        """
        ticketbox = self._get_ticketbox_for_ticket(item)
        state = ticketbox.get_state_by_id(item.getState)

        if not state:
            return '-'
        else:
            return state.get('title', '-')

    def __init__(self, context, request):
        super(TabbedTicketBoxOverviewBaseView, self).__init__(context, request)

        self.columns = ({'column': 'Title',
                        'column_title': _(u"Title"),
                        'sort_index': 'sortable_title',
                        'transform': self.izug_files_linked,
                        },
                        {'column': 'getResponsibleManager',
                         'column_title': _(u"Responsible"),
                         'sort_index': 'sortable_responsibleManager',
                         'transform': self.readable_responsibleManager,
                        },
                        {'column': 'getState',
                        'column_title': _(u"State"),
                        'transform': self.map_state,
                        },
                        {'column': 'Creator',
                         'column_title': _(u"Creator"),
                         'transform': readable_author,
                        },
                        )

    def search(self, kwargs):
        """Custom search method for ticketbox
        """
        membership = self.context.aq_inner.portal_membership
        member_id = membership.getAuthenticatedMember().getId()

        # show only tickets, where creater is me
        if self.filter_my_created_tickets:
            kwargs['Creator'] = member_id

        # show only tickets, where ResponsibleManager is me
        if self.filter_responsibleManager:
            kwargs['responsibleManager'] = member_id

        self.catalog = catalog = getToolByName(self.context, 'portal_catalog')
        query = self.build_query(**kwargs)
        brains = catalog(**query)

        # Filter by state (ATField State not review_state)
        if not self.filter_state:
            self.contents = brains
        else:
            self.contents = filter(self._should_ticket_be_listed, brains)

        self.len_results = len(self.contents)

    def build_query(self, *args, **kwargs):
        """ Override build_query of baseclass.
        We need to search the whole site and not on the context's path
        """

        query = {}
        query.update(kwargs)
        sort_on = kwargs.get('sort_on')
        index = self.catalog._catalog.indexes.get(sort_on, None)
        if index is not None:
            index_type = index.__module__
            if index_type in self.custom_sort_indexes:
                del query['sort_on']
                del query['sort_order']
                self._custom_sort_method = \
                    self.custom_sort_indexes.get(index_type)
        return query
