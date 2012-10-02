from ftw.upgrade import ProgressLogger
from ftw.upgrade import UpgradeStep
import logging


LOG = logging.getLogger('izug.ticketbox.upgrades')


class MigrateTicketDescription(UpgradeStep):

    def __call__(self):
        catalog = self.getToolByName('portal_catalog')
        brains = catalog.unrestrictedSearchResults(
            portal_type='Ticket')

        title = 'Migrate ticket description to rich text field'
        with ProgressLogger(title, brains) as step:

            for brain in brains:
                self._migrate_description(brain)
                step()

    def _migrate_description(self, brain):
        obj = self.portal.unrestrictedTraverse(brain.getPath())

        field = obj.getField('description')
        field.set(obj, field.getRaw(obj))
