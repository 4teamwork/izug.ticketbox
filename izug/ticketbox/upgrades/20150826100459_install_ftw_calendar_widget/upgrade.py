from ftw.upgrade import UpgradeStep


class InstallFtwCalendarWidget(UpgradeStep):
    """Install ftw calendar widget.
    """

    def __call__(self):
        self.setup_install_profile('profile-ftw.calendarwidget:default')
