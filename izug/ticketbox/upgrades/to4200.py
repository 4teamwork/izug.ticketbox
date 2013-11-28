from ftw.upgrade import UpgradeStep
from izug.ticketbox.content.attachment import TicketAttachment
import logging


LOG = logging.getLogger('ftw.workspace.upgrades')


class UpdateTicketAttachmentClass(UpgradeStep):

    def __call__(self):
        self.update_fti()
        self.migrate_existing_attachments()

    def update_fti(self):
        LOG.info('TabbedViewFolder FTI: update factory')
        self.setup_install_profile(
            'profile-izug.ticketbox.upgrades:4200')

    def migrate_existing_attachments(self):
        query = {'portal_type': 'TicketAttachment'}
        for obj in self.objects(query, "Migrate TicketAttachment class"):
            self.migrate_class(obj, TicketAttachment)
