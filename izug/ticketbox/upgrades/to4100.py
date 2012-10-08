from ftw.upgrade import ProgressLogger
from ftw.upgrade import UpgradeStep
import logging


LOG = logging.getLogger('izug.ticketbox.upgrades')


class AddTicketboxTitleIndex(UpgradeStep):

    def __call__(self):
        self.import_catalog()
        self.add_catalog_index()
        self.add_update_catalog()

    def import_catalog(self):
        self.setup_install_profile('profile-izug.ticketbox.upgrades:4100')

    def add_catalog_index(self):
        if not self.catalog_has_index('ticketbox_title'):
            self.catalog_add_index('ticketbox_title', 'FieldIndex')

    def add_update_catalog(self):
        query = {'portal_type': 'Ticket'}
        objects = self.catalog_unrestricted_search(query, full_objects=True)

        with ProgressLogger('Reindex tickets', objects) as step:
            for obj in objects:
                obj.reindexObject(idxs=['ticketbox_title'])
                step()
