from ftw.upgrade import UpgradeStep


class EnableXlsxExport(UpgradeStep):

    def __call__(self):
        self.setup_install_profile('profile-izug.ticketbox.upgrades:4202')
