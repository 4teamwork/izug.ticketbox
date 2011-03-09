from ftw.tabbedview.browser.views import views
from izug.ticketbox import ticketboxMessageFactory as _



class TabbedTicketBoxView(views.TabbedView):

    filter_state = True
    show_searchform = True

    def get_tabs(self):
        return [{'id':_(u'Overview'), 'class':''},
                {'id':_(u'all_tickets'),'class':''},
                {'id':_(u'my_tickets'),'class':''},
                # {'id':'Meetings','class':''},
               ]


