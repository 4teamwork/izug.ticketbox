from poi_ticketbox_migration import \
    PoiIssueToTicketboxTicket, \
    PoiTrackerToTicketbox
from update_references import UpdateReferences
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from StringIO import StringIO
from zope.app.pagetemplate import ViewPageTemplateFile
import logging


class MigrationPoiTicketbox(BrowserView):

    template = ViewPageTemplateFile('migration_poi_ticketbox.pt')

    def __call__(self):
        """"""

        if self.request.get('convert'):

            self.logger = logging.getLogger('izug.ticketbox')
            self.logger.info("\n\nStarting migration " \
                "\n----------------------" \
                "\n * Convert Ticketbox" \
                "\n * Update Catalog" \
                "\n * Convert Tickets and Responses" \
                "\n * Update Catalog" \
                "\n * Update References" \
                "\n----------------------")

            self.portal_site = getToolByName(
                self.context, 'portal_url').getPortalObject()

            # Path to the Poi-Tracker you want to migrate
            self.src_path = self.request.get('src_path')

            # Create a map for old and new user-ids
            self.mapping = self.map_users(
                self.request.get('user_mapping'))

            # Start migrate Ticketbox
            self.migrate_ticketbox()

            # Start migrate Tickets and Responses
            self.migrate_ticket()


        return self.template()

    def map_users(self, mapping):
        """return a usermapping for the poi-ticketbox-migration"""

        user_mapping = {}
        rows = mapping.split('\r\n')
        for row in rows:
            cols = row.split(',')
            user_mapping[cols[0]] = cols[1]
        return user_mapping

    def get_paths(self, src_path, src_type):
        """get all paths to childrenobjects"""

        catalog = self.context.portal_catalog
        brains = catalog({'portal_type': src_type, 'path': src_path})
        paths = []

        for brain in brains:
            paths.append(brain.getPath())

        return paths

    def migrate_ticketbox(self):
        """Ticketbox migration"""

        migr_obj = PoiTrackerToTicketbox
        src_query = {
            'portal_type': migr_obj.src_meta_type,
            'path': self.src_path,
            'sort_on': 'id'}

        self.logger.info("Start convert tracker at %s" % self.src_path)

        self.start_convert(migr_obj, src_query)

    def migrate_ticket(self):
        """Ticket and response migration"""

        migr_obj = PoiIssueToTicketboxTicket
        migr_obj.user_mapping = self.mapping

        path = self.get_paths(self.src_path, migr_obj.src_meta_type)

        src_query = {
            'portal_type': migr_obj.src_meta_type,
            'path': path,
            'sort_on': 'id'}

        self.logger.info("Start convert Issues for Tracker at %s" % self.src_path)

        self.start_convert(migr_obj, src_query)

    def start_convert(self, migr_obj, src_query):
        # Start to convert the tickets and answers
        walker = migr_obj.walker(
            self.portal_site.context,
            migr_obj,
            query=src_query)

        out = StringIO()

        walker.go(out=out)
        print >> out, walker.getOutput()
        self.logger.info("Converting complete")
        self.logger.info('Start update catalog')
        self.context.portal_catalog.refreshCatalog()
        self.logger.info("Catalog update complete")

    def update_references(self, paths):
        """update references for tikets"""

        for path in paths:
            pass
            # ticket = self.restrictedTraverse(path)
