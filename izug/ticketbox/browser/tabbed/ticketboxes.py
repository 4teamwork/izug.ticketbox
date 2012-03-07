from Products.CMFCore.utils import getToolByName
from ftw.tabbedview.browser.listing import CatalogListingView
from ftw.tabbedview.browser.tabbed import TabbedView
from ftw.table import helper
from izug.ticketbox import ticketboxMessageFactory as _
from izug.ticketbox.browser.tabbed.base import BaseTicketListingTab
import os.path


class TicketboxesTabbedView(TabbedView):

    def get_tabs(self):
        return (
            {'id': _('global-ticketboxes'),
             'class': ''},

            {'id': _('global-all_tickets'),
             'class': ''},

            {'id': _('global-my_tickets'),
             'class': ''},

            {'id': _('global-my_issued_tickets'),
             'class': ''},
            )


class GlobalTicketboxesTab(CatalogListingView):

    types = ['Ticket Box']
    show_selects = False
    sort_on = 'sortable_title'

    enabled_actions = major_actions = ['reset_tableconfiguration']

    columns = (
        {'column': 'Title',
         'column_title': _(u"Title"),
         'sort_index': 'sortable_title',
         'transform': helper.linked_without_icon},

        {'column': 'modified',
         'column_title': _(u"ModificationDate"),
         'transform': helper.readable_date},

        {'column': 'ownerid',
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

    def get_base_query(self):
        site = getToolByName(self.context, 'portal_url').getPortalObject()
        site_path = '/'.join(site.getPhysicalPath())

        query = super(GlobalTicketTabBase, self).get_base_query()
        query['path']['query'] = site_path
        return query

    def _get_ticketbox_path_for(self, item):
        path = item.getPath()
        path, ticketid_ = os.path.split(path)
        return path


class GlobalAllTicketsTab(GlobalTicketTabBase):
    """Global tickets tab listing all (visible) tickets.
    """


class GlobalMyTicketsTab(GlobalTicketTabBase):
    """Tab listing all tickets where the current user is responsible.
    """

    def get_base_query(self):
        query = super(GlobalMyTicketsTab, self).get_base_query()

        member = self.context.restrictedTraverse('@@plone_portal_state').member()
        query['getResponsibleManager'] = member.getId()

        return query


class GlobalMyIssuedTicketsTab(GlobalTicketTabBase):
    """Tab listing all tickets where the current user is the creator.
    """

    def get_base_query(self):
        query = super(GlobalMyIssuedTicketsTab, self).get_base_query()

        member = self.context.restrictedTraverse('@@plone_portal_state').member()
        query['Creator'] = member.getId()

        return query