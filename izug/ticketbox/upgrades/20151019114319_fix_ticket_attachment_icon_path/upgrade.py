from ftw.upgrade import UpgradeStep


class FixTicketAttachmentIconPath(UpgradeStep):
    """Fix ticket attachment icon path.
    """

    def __call__(self):
        self.install_upgrade_profile()
