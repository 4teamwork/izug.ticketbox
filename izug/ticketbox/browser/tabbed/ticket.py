from ftw.tabbedview import tabbedviewMessageFactory
from ftw.tabbedview.browser.tabbed import TabbedView
from izug.ticketbox import ticketboxMessageFactory as _
from izug.ticketbox.interfaces import ISubTicket


class TicketTabbedView(TabbedView):

    def get_tabs(self):
        tabs = [
            {'id': _('ticket'),
             'class': ''},

            {'id': _('attachments'),
             'class': ''},
            ]

        if not ISubTicket.providedBy(self.context):
            tabs.append({'id': tabbedviewMessageFactory('issued_subtickets'),
                         'class': ''})

        return tabs
