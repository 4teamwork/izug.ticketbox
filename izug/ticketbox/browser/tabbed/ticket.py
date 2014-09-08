from ftw.tabbedview.browser.tabbed import TabbedView
from izug.ticketbox import ticketboxMessageFactory as _


class TicketTabbedView(TabbedView):

    def get_tabs(self):
        return (
            {'id': _('ticket'),
             'class': ''},

            {'id': _('attachments'),
             'class': ''},
            )
