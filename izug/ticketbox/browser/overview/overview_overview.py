from baseview import TabbedTicketBoxOverviewBaseView
from izug.ticketbox import ticketboxMessageFactory as _
from ftw.table import helper


class TicketBoxOverview(TabbedTicketBoxOverviewBaseView):
    """ Overview-view for Ticketboxes.
    We use this view to list all Ticketboxes in a Plonesite
    """
    types = 'Ticket Box'
    columns = None
    sort_on = 'sortable_title'

    def __init__(self, context, request):
        super(TicketBoxOverview, self).__init__(context, request)

        self.columns = ({'column': 'Title',
                        'column_title': _(u"Title"),
                        'sort_index': 'sortable_title',
                        'transform': self.izug_files_linked,
                        },
                        {'column': 'modified',
                         'column_title': _(u"ModificationDate"),
                         'transform': helper.readable_date,
                        },
                        {'column': 'Creator',
                         'column_title': _(u"Responsible"),
                         'transform': helper.readable_author,
                        },
                        )
