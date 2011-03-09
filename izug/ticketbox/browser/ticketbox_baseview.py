from Products.CMFCore.utils import getToolByName
from izug.arbeitsraum.browser.views import MyListing

class TabbedTicketBoxBaseView(MyListing):

    resonsibleManager = None
    filter_state = None

    request_filters = [
        ('responsibleManager', 'responsible', None),
        ('State', 'state', None),
        ('Releases', 'release', None),
        ('Area', 'area', None),
        ('Priority', 'priority', None),
        ]

    def search(self, kwargs):
        """Custom search method for ticketbox"""
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

