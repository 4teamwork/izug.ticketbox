from Products.Five import BrowserView
from StringIO import StringIO
from poi_ticketbox_migration import PoiIssueToTicketboxTicket
from zope.app.pagetemplate import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName


class MigrationPoiTicketbox(BrowserView):

    template = ViewPageTemplateFile('migration_poi_ticketbox.pt')

    def __call__(self):
        """"""

        if self.request.get('convert'):
            portal = getToolByName(self.context, 'portal_url').getPortalObject()
            migr_obj = PoiIssueToTicketboxTicket
            src_path = self.request.get('src_path')
            dest_path = self.request.get('dest_path')
            src_type = self.request.get('src_type')
            dest_type = self.request.get('dest_type')
            src_parent_type = self.request.get('src_parent_type')
            dest_parent_type = self.request.get('dest_parent_type')
            path = self.get_paths(src_path, src_type)

            src_query = {'portal_type' : src_type, 'path' : path, 'sort_on' : 'id'}
            dest_query = src_query.copy()
            dest_query['portal_type'] = dest_type

            print "start convert"
            out = StringIO()

            walker = migr_obj.walker(portal, migr_obj, query=src_query)
            walker.go(out=out)
            print >> out, walker.getOutput()
            print "finished convert"
            self.context.portal_catalog.refreshCatalog()
            print "catalog updated"

            #
            # print "copy to dest"
            # self.copy_to_dest(src_parent_type, dest_parent_type, dest_type, src_path, dest_path)

        return self.template()
    #
    # def copy_to_dest(self, src_parent_type, dest_parent_type, dest_type, src_path, dest_path):
    #     """copy the tickets to the destination folder"""
    #
    #     catalog = self.context.portal_catalog
    #
    #     src_parent = catalog({'portal_type': src_parent_type, 'path': src_path})[0].getObject()
    #     dest_parent = catalog({'portal_type': dest_parent_type, 'path': dest_path})[0].getObject()
    #
    #     ids = []
    #
    #     for i in catalog(path=src_path,portal_type=dest_type)[:]:
    #          ids.append(i.getId)
    #
    #     cb_copy_data = src_parent.manage_copyObjects(ids)
    #     dest_parent.manage_pasteObjects(cb_copy_data)
    #     catalog.refreshCatalog()

    def get_paths(self, src_path, src_type):
        """get all paths to childreenobjects"""

        catalog = self.context.portal_catalog
        brains = catalog({'portal_type': src_type, 'path': src_path})
        paths = []

        for brain in brains:
            paths.append(brain.getPath())

        return paths
