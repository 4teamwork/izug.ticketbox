from izug.ticketbox.browser.helper import map_attribute, readable_author
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class TicketView(BrowserView):

    template = ViewPageTemplateFile('ticket_view.pt')

    # HELPER Methods for ftw.table generator
    def map_state(self):
        """
        search the title-name of a list with the id
        """
        return map_attribute(self.context, "state")

    def map_priority(self):
        """
        search the title-name of a list with the id
        """
        return map_attribute(self.context, "priority")

    def map_area(self):
        """
        search the title-name of a list with the id
        """
        return map_attribute(self.context, "area")

    def map_variety(self):
        """
        search the title-name of a list with the id
        """
        return map_attribute(self.context, "variety")

    def map_release(self):
        """
        search the title-name of a list with the id
        """
        return map_attribute(self.context, "releases")

    def map_watched_release(self):
        """
        search the title-name of a list with the id
        """
        return map_attribute(self.context, "watchedRelease")

    def map_author(self):
        """
        get the full name of a user-id
        """
        return readable_author(self.context)
