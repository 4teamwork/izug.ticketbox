from ftw.tabbedview.browser.listing import CatalogListingView
from ftw.table import helper
from izug.ticketbox import ticketboxMessageFactory as _
from izug.ticketbox.browser.tabbed.base import BaseTicketListingTab
from izug.ticketbox.browser.ticket_view import TicketView
from Products.CMFCore.utils import getToolByName


def icon(item, value):
    img = u'<img src="%s/%s"/>' % (item.portal_url(), item.getIcon)
    link = u'<a href="%s/at_download">%s</a>' % (item.getURL(), img)
    return link


def linked_attachment(item, title):
    return '<a href="%s/at_download/file">%s</a>' % (
        item.getURL(), title)


def attachment_ticketnr(item, nothing):
    url = item.getURL()
    split_url = url.split("/")

    if len(split_url) >= 2:
        ticket_url = '/'.join(split_url[:-1])
        return '<a href="%s"># %s</a>' % (ticket_url, split_url[-2])

    else:
        return id


class AllTicketsTab(BaseTicketListingTab):
    """Tab listing all tickets and sub tickets in this ticketbox.
    """

    types = ['Ticket', 'SubTicket']

    def get_base_query(self):
        query = super(AllTicketsTab, self).get_base_query()

        query['getState'] = [state['id']
                             for state in self.context.getAvailableStates()
                             if state['show_in_all_tickets'] == '1']

        return query


class MyTicketsTab(BaseTicketListingTab):
    """Tab listing all tickets where the current user is responsible.
    """

    types = ['Ticket', 'SubTicket']

    def get_base_query(self):
        query = super(MyTicketsTab, self).get_base_query()

        member = self.context.restrictedTraverse(
            '@@plone_portal_state').member()
        query['getResponsibleManager'] = member.getId()
        query['getState'] = [state['id']
                             for state in self.context.getAvailableStates()
                             if state['show_in_my_tickets'] == '1']

        return query


class MyIssuedTicketsTab(BaseTicketListingTab):
    """Tab listing all tickets and sub ticketswhere the current user is the
    creator.
    """

    types = ['Ticket', 'SubTicket']

    def get_base_query(self):
        query = super(MyIssuedTicketsTab, self).get_base_query()

        member = self.context.restrictedTraverse(
            '@@plone_portal_state').member()
        query['Creator'] = member.getId()
        query['getState'] = [state['id']
                             for state in self.context.getAvailableStates()
                             if state['show_in_my_tickets'] == '1']

        return query


def get_current_user_id(context):
    portal_membership = getToolByName(context, 'portal_membership')
    user = portal_membership.getAuthenticatedMember()
    return user.getId()


class MyIssuedSubTicketsTab(BaseTicketListingTab):

    types = ['SubTicket']
    search_options = {'Creator': get_current_user_id}


class MyIssuedSubTicketsAllBoxesTag(MyIssuedSubTicketsTab):
    """This tab view lists all sub tickets from all ticket boxes
    created by the current user.
    """

    def _get_cached_options_for(self, item, getter_name):
        """Returns all available options for the field with the
        getter name `getter_name` of the ticket box of the
        current item.
        """
        if self._cached_ticketbox_options is None:
            self._cached_ticketbox_options = {}

        catalog = getToolByName(self.context, 'portal_catalog')
        boxes = [brain.getObject() for brain
                 in catalog(portal_type="Ticket Box")]

        for box in boxes:
            box_path = self._get_ticketbox_path_for(box)
            if box_path not in self._cached_ticketbox_options:
                self._cached_ticketbox_options[box_path] = {}
            box_cache = self._cached_ticketbox_options[box_path]

            if getter_name not in box_cache:
                box_cache[getter_name] = {}
            box = self.context.unrestrictedTraverse(box_path)
            for option in getattr(box, getter_name)():
                box_cache[getter_name][option['id']] = option['title']

        return box_cache[getter_name]

    def _get_ticketbox_path_for(self, item):
        """Returns the ticketbox path for an item.
        """
        return '/'.join(item.getPhysicalPath())


class AttachmentsTab(CatalogListingView):

    types = ['File']

    show_selects = False
    show_menu = False

    sort_on = 'sortable_title'

    columns = (
        {'column': 'Type',
         'column_title': _(u"Type"),
         'sort_index': 'getContentType',
         'transform': icon,
         },

        {'column': 'Title',
         'column_title': _(u"Title"),
         'sort_index': 'sortable_title',
         'transform': linked_attachment,
         },

        # There is no index ticket-number. Use the helper for getting it.
        {'column': 'ticket-number',
         'column_title': _(u"Ticketnr"),
         'sort_index': 'sortable_ticket_references',
         'transform': attachment_ticketnr,
         })


class TicketboxesTab(CatalogListingView):

    types = ['Ticket Box']
    show_selects = False
    show_menu = False
    sort_on = 'sortable_title'

    columns = (
        {'column': 'Title',
         'column_title': _(u"Title"),
         'sort_index': 'sortable_title',
         'transform': linked_attachment},

        {'column': 'modified',
         'column_title': _(u"ModificationDate"),
         'transform': helper.readable_date},

        {'column': 'get_owner_index',
         'column_title': _(u"Responsible"),
         'transform': helper.readable_author},
        )


class TicketTab(TicketView):
    pass
