from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ticketbox_baseview import TabbedTicketBoxBaseView, readable_author
from ftw.table import helper
from izug.arbeitsraum.browser.views import izug_files_linked

class TicketBoxView(TabbedTicketBoxBaseView):

    template = ViewPageTemplateFile('ticketbox_view.pt')
    types = 'Ticket'
    #this is a attribute in the DataGrid States from TicketBox ContentType
    sort_on = 'getId'
    columns = None

    def __init__(self, context, request):
        super(TicketBoxView, self).__init__(context, request)

        self.columns = (
                     ('getId', 'getId',),
                     ('Title', 'sortable_title', izug_files_linked),
                     ('responsibleManager', 'responsibleManager',readable_author),
                     ('State', 'State', self.map_state),
                     ('Due_date', 'Due_date', helper.readable_date_time_text),
                     ('Priority', 'Priority', self.map_priority),
                     ('Area', 'Area', self.map_area),
                 )


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

        # Playing nicely with the form.

        # Subject can be a string of one tag, a tuple of several tags
        # or a dict with a required query and an optional operator
        # 'and/or'.  We must avoid the case of the dict with only the
        # operator and no actual query, else we will suffer from
        # KeyErrors.  Actually, when coming from the
        # poi_issue_search_form, instead of say from a test, its type
        # is not 'dict', but 'instance', even though it looks like a
        # dict.  See http://plone.org/products/poi/issues/137
        if 'Subject' in query:
            subject = query['Subject']
            # We cannot use "subject.has_key('operator')" or
            # "'operator' in subject'" because of the strange
            # instance.
            try:
                op = subject['operator']
            except TypeError:
                # Fine: subject is a string or tuple.
                pass
            except KeyError:
                # No operator, so nothing can go wrong.
                pass
            else:
                try:
                    dummy = subject['query']
                except KeyError:
                    del query['Subject']

        query['sort_on'] = criteria.get('sort_on', 'created')
        query['sort_order'] = criteria.get('sort_order', 'reverse')
        if criteria.get('sort_limit'):
            query['sort_limit'] = criteria.get('sort_limit')
        return query