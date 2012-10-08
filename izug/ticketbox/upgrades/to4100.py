from ftw.upgrade import UpgradeStep


class AddTicketboxTitleIndex(UpgradeStep):

    def __call__(self):
        self.setup_install_profile('profile-izug.ticketbox.upgrades:4100')
        self.catalog_reindex_objects({'portal_type': 'Ticket'},
                                     idxs=['ticketbox_title'])
