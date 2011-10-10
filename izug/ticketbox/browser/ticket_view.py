from DateTime import DateTime
from izug.ticketbox.browser.helper import map_attribute, readable_responsibleManager, readable_username
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

    def map_release(self):
        """
        search the title-name of a list with the id
        """
        return map_attribute(self.context, "releases")

    def map_author(self):
        """
        get the full name of a user-id
        """
        return readable_responsibleManager(self.context)

    def map_creator(self):
        """
        get the full name of the creator
        """
        return readable_username(self.context, self.context.Creator())

    def get_creation_date(self):
        """
        Return the creation date as a datetime object
        """
        return DateTime(self.context.CreationDate())