from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class TicketBoxView(BrowserView):

    template = ViewPageTemplateFile('ticketbox_view_all_tickets.pt')

