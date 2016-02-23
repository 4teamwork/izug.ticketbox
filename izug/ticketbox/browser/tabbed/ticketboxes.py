from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName
from ftw.tabbedview.browser.listing import CatalogListingView
from ftw.tabbedview.browser.tabbed import TabbedView
from ftw.table import helper
from izug.ticketbox import ticketboxMessageFactory as _
from izug.ticketbox.browser.tabbed.base import BaseTicketListingTab
import os.path


def link_to_parent(item, value):
    """Tabbedview helper for linking the parent.
    """

    if isinstance(value, str):
        value = value.decode('utf-8')

    parent = aq_parent(aq_inner(item.getObject()))
    title = parent.Description().decode('utf-8')

    return u'<a href="%s" title="%s">%s</a>' % (
        os.path.dirname(item.getURL()),
        title,
        value)


class TicketboxesTabbedView(TabbedView):

    def get_tabs(self):
        return (
            {'id': _('global-my_tickets'),
             'class': ''},

            {'id': _('global-my_issued_tickets'),
             'class': ''},

            {'id': _('global-all_tickets'),
             'class': ''},

            {'id': _('global-ticketboxes'),
             'class': ''},
        )


class GlobalTicketboxesTab(CatalogListingView):

    types = ['Ticket Box']
    show_selects = False
    show_menu = False
    sort_on = 'sortable_title'

    columns = (
        {'column': 'Title',
         'column_title': _(u"Title"),
         'sort_index': 'sortable_title',
         'transform': helper.linked},

        {'column': 'modified',
         'column_title': _(u"ModificationDate"),
         'transform': helper.readable_date},

        {'column': 'get_owner_index',
         'column_title': _(u"Responsible"),
         'transform': helper.readable_author},
    )

    def get_base_query(self):
        site = getToolByName(self.context, 'portal_url').getPortalObject()
        site_path = '/'.join(site.getPhysicalPath())

        query = super(GlobalTicketboxesTab, self).get_base_query()
        query['path']['query'] = site_path
        return query


class GlobalTicketTabBase(BaseTicketListingTab):

    @property
    def columns(self):
        columns = list(super(GlobalTicketTabBase, self).columns)
        columns.append({'column': 'ticketbox_title',
                        'column_title': _(u'Ticket Box'),
                        'transform': link_to_parent})
        return tuple(columns)

    def get_base_query(self):
        site = getToolByName(self.context, 'portal_url').getPortalObject()
        site_path = '/'.join(site.getPhysicalPath())

        query = super(GlobalTicketTabBase, self).get_base_query()
        query['path']['query'] = site_path
        return query

    def _get_ticketbox_path_for(self, item):
        path = item.getPath()
        path, _ticketid = os.path.split(path)
        return path


class GlobalAllTicketsTab(GlobalTicketTabBase):
    """Global tickets tab listing all (visible) tickets.
    """


class GlobalMyTicketsTab(GlobalTicketTabBase):
    """Tab listing all tickets where the current user is responsible.
    """

    def get_base_query(self):
        query = super(GlobalMyTicketsTab, self).get_base_query()

        member = self.context.restrictedTraverse(
            '@@plone_portal_state').member()
        query['getResponsibleManager'] = member.getId()

        return query


class GlobalMyIssuedTicketsTab(GlobalTicketTabBase):
    """Tab listing all tickets where the current user is the creator.
    """

    def get_base_query(self):
        query = super(GlobalMyIssuedTicketsTab, self).get_base_query()

        member = self.context.restrictedTraverse(
            '@@plone_portal_state').member()
        query['Creator'] = member.getId()

        return query
