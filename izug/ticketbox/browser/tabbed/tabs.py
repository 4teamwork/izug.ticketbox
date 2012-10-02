from ftw.tabbedview.browser.listing import CatalogListingView
from ftw.table import helper
from izug.ticketbox import ticketboxMessageFactory as _
from izug.ticketbox.browser.tabbed.base import BaseTicketListingTab


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
    """Tab listing all tickets in this ticketbox.
    """

    def get_base_query(self):
        query = super(AllTicketsTab, self).get_base_query()

        query['getState'] = [state['id']
                             for state in self.context.getAvailableStates()
                             if state['show_in_all_tickets'] == '1']

        return query


class MyTicketsTab(BaseTicketListingTab):
    """Tab listing all tickets where the current user is responsible.
    """

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
    """Tab listing all tickets where the current user is the creator.
    """

    def get_base_query(self):
        query = super(MyIssuedTicketsTab, self).get_base_query()

        member = self.context.restrictedTraverse(
            '@@plone_portal_state').member()
        query['Creator'] = member.getId()
        query['getState'] = [state['id']
                             for state in self.context.getAvailableStates()
                             if state['show_in_my_tickets'] == '1']

        return query


class AttachmentsTab(CatalogListingView):

    types = ['TicketAttachment']

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
