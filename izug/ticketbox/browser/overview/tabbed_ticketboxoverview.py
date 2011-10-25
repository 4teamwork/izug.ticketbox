from ftw.tabbedview.browser.views import views
from izug.ticketbox import ticketboxMessageFactory as _


class TabbedTicketBoxOverviewView(views.TabbedView):

    filter_state = True
    show_searchform = True

    def get_tabs(self):
        translate = self.context.translate
        return [{'id':'Overview', 'class':'',
                'description': translate(_('msg_overviewDescription',
                                           default='Displays the Overview'))},
                {'id':'all_tickets', 'class':'',
                 'description': translate(_('msg_allTicketsDescription',
                                            default='Displays all Ticket'))},
                {'id':'my_tickets', 'class':'',
                 'description': translate(_('msg_myTicketsDescription',
                                            default='Displays your Tickets'))},
               ]
