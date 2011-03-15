from izug.ticketbox import ticketboxMessageFactory as _
from izug.ticketbox.browser.helper import map_attribute
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class TicketView(BrowserView):

    template = ViewPageTemplateFile('ticket_view.pt')

    # HELPER Methods for ftw.table generator
    def map_state(self):
        """
        search the title-name of a list with the id
        """
        return map_attribute(self.context, "State")

    def map_priority(self):
        """
        search the title-name of a list with the id
        """
        return map_attribute(self.context, "Priority")

    def map_area(self):
        """
        search the title-name of a list with the id
        """
        return map_attribute(self.context, "Area")

    def map_release(self):
        """
        search the title-name of a list with the id
        """
        return map_attribute(self.context, "Releases")

    def readable_author(self):
        """
        get the full name of a user-id
        """

        author = self.context.responsibleManager
        if not author:
            return '-'
        name = author
        user = self.context.acl_users.getUserById(author)
        if user is None:
            return _(u"unassigned")
        else:
            name = user.getProperty('fullname', author)
            if not len(name):
                name = author
            return name
