from izug.arbeitsraum.browser.views import InfoView
from Acquisition import aq_inner
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from plone.app.workflow.interfaces import ISharingPageRole
from zope.component import getUtilitiesFor
from izug.ticketbox import ticketboxMessageFactory as _
from ticketbox_baseview import TabbedTicketBoxBaseView

class TicketBoxInfoView(TabbedTicketBoxBaseView):
    """Info Tabbview
    """
    template = ViewPageTemplateFile('ticketbox_view_info_view.pt')
    def roles(self):
        """Get a list of roles that can be managed.

        Returns a list of dicts with keys:

            - id
            - title
        """
        context = aq_inner(self.context)

        pairs = []
        has_manage_portal = context.portal_membership.checkPermission('ManagePortal', context)
        aviable_roles_for_users = [u'Editor', u'Reader', u'Contributor', u'Administrator']
        for name, utility in getUtilitiesFor(ISharingPageRole):
            if not has_manage_portal and name not in aviable_roles_for_users:
                continue
            pairs.append(dict(id = name, title = utility.title))

        pairs.sort(key=lambda x: x["id"])
        return pairs

    def role_settings(self):
        context = self.context
        results = super(InfoView, self).role_settings()

        if not context.portal_membership.checkPermission('ManagePortal', context):
            results = [r for r in results if r['type']!='group']

        return results

    def description(self):
        """docstring"""
        translated = self.context.translate(_(u'tooltip_info'))
        if translated == u'tooltip_info':
            return ''
        else:
            return translated