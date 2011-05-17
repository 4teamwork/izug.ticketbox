from Products.Five import BrowserView
from StringIO import StringIO
from poi_ticketbox_migration import PoiIssueToTicketboxTicket, PoiTrackerToTicketbox
from zope.app.pagetemplate import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName


class MigrationPoiTicketbox(BrowserView):

    template = ViewPageTemplateFile('migration_poi_ticketbox.pt')

    def __call__(self):
        """"""

        if self.request.get('convert'):
            self.portal_site = getToolByName(self.context, 'portal_url').getPortalObject()
            self.src_path = self.request.get('src_path')
            self.migrate_ticketbox()
            self.migrate_ticket()
        return self.template()


    def get_paths(self, src_path, src_type):
        """get all paths to childrenobjects"""

        catalog = self.context.portal_catalog
        brains = catalog({'portal_type': src_type, 'path': src_path})
        paths = []

        for brain in brains:
            paths.append(brain.getPath())

        return paths

    def migrate_ticketbox(self):
        migr_obj = PoiTrackerToTicketbox
        src_query = {'portal_type' : migr_obj.src_meta_type, 'path' : self.src_path, 'sort_on' : 'id'}

        print "start convert Tracker"
        out = StringIO()

        walker = migr_obj.walker(self.portal_site.context, migr_obj, query=src_query)

        walker.go(out=out)
        print >> out, walker.getOutput()
        print "finished convert"
        self.context.portal_catalog.refreshCatalog()
        print "catalog updated"

    def migrate_ticket(self):

        migr_obj = PoiIssueToTicketboxTicket

        path = self.get_paths(self.src_path, migr_obj.src_meta_type)

        src_query = {'portal_type' : migr_obj.src_meta_type, 'path' : path, 'sort_on' : 'id'}
        dest_query = src_query.copy()
        dest_query['portal_type'] = migr_obj.dst_meta_type

        print "start convert Issues"
        out = StringIO()

        walker = migr_obj.walker(self.portal_site.context, migr_obj, query=src_query)
        walker.go(out=out)
        print >> out, walker.getOutput()
        print "finished convert"
        self.context.portal_catalog.refreshCatalog()
        print "catalog updated"
