from ftw.upgrade import UpgradeStep


class FixIconsForTicketAndTicketBox(UpgradeStep):
    """Fix icons for ticket and ticket box.
    """

    def __call__(self):
        self.install_upgrade_profile()
