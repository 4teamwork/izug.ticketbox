from Acquisition import aq_inner
from plone.app.workflow.interfaces import ISharingPageRole
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import getUtilitiesFor
from plone.app.workflow.browser.sharing import SharingView


class TicketBoxInfoView(SharingView):
    """Info Tabbview
    """
    template = ViewPageTemplateFile('info_view.pt')

    def roles(self):
        """Get a list of roles that can be managed.

        Returns a list of dicts with keys:

            - id
            - title
        """
        context = aq_inner(self.context)

        pairs = []
        has_manage_portal = context.portal_membership.checkPermission(
            'ManagePortal', context)

        aviable_roles_for_users = [
            u'Editor',
            u'Reader',
            u'Contributor',
            u'Administrator']

        for name, utility in getUtilitiesFor(ISharingPageRole):
            if not has_manage_portal and name not in aviable_roles_for_users:
                continue
            pairs.append(dict(id = name, title = utility.title))

        pairs.sort(key=lambda x: x["id"])
        return pairs

    def role_settings(self):
        context = self.context
        results = super(TicketBoxInfoView, self).role_settings()

        if not context.portal_membership.checkPermission(
            'ManagePortal', context):

            results = [r for r in results if r['type']!='group']

        return results