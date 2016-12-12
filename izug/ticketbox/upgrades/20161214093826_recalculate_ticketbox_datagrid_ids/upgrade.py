from ftw.upgrade import UpgradeStep
from izug.ticketbox.interfaces import ITicketboxDatagridIdUpdater


class RecalculateTicketboxDatagridIds(UpgradeStep):
    """Recalculate ticketbox datagrid ids.
    """

    def __call__(self):
        self.install_upgrade_profile()
        for obj in self.objects(
                {'portal_type': 'Ticket Box'},
                'Recalculate ticketbox datagrid ids'):
            ITicketboxDatagridIdUpdater(obj)()
