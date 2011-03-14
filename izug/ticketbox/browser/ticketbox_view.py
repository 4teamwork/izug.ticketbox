from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ticketbox_baseview import TabbedTicketBoxBaseView

class TicketBoxView(TabbedTicketBoxBaseView):

    template = ViewPageTemplateFile('ticketbox_view.pt')
    types = 'Ticket'
    #this is a attribute in the DataGrid States from TicketBox ContentType
    columns = None

    def getFilteredTickets(self, criteria=None, **kwargs):
        """Get the contained issues in the given criteria.
        """
        context = aq_inner(self.context)
        query = self.buildIssueSearchQuery(criteria, **kwargs)
        catalog = getToolByName(context, 'portal_catalog')
        return catalog.searchResults(query)

    def buildIssueSearchQuery(self, criteria=None, **kwargs):
        """Build canonical query for issue search.
        """
        context = aq_inner(self.context)
        if criteria is None:
            criteria = kwargs
        else:
            criteria = dict(criteria)

        allowedCriteria = {'release'       : 'Releases',
                           'area'          : 'Area',
                           'issueType'     : 'getIssueType',
                           'priority'      : 'Priority',
                           'state'         : 'State',
                           'responsible'   : 'responsibleManager',
                           'creator'       : 'Creator',
                           'text'          : 'SearchableText',
                           'id'            : 'getId',
                           }

        query                = {}
        query['path']        = '/'.join(context.getPhysicalPath())
        query['portal_type'] = ['Ticket']

        for k, v in allowedCriteria.items():
            if k in criteria:
                query[v] = criteria[k]
            elif v in criteria:
                query[v] = criteria[v]


        query['sort_on'] = criteria.get('sort_on', 'created')
        query['sort_order'] = criteria.get('sort_order', 'reverse')
        if criteria.get('sort_limit'):
            query['sort_limit'] = criteria.get('sort_limit')
        return query