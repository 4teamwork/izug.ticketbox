from ftw.upgrade import UpgradeStep


class AddTabForInactiveTickets(UpgradeStep):
    """Add tab for inactive tickets.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.actions_add_type_action(
            portal_type='Ticket Box', after='my_tickets',
            action_id='inactive_tickets', visible=True,
            action='string:${object_url}#inactive_tickets',
            title="Inactive tickets", category="tabbedview-tabs",
            condition="", permissions=('View',))
