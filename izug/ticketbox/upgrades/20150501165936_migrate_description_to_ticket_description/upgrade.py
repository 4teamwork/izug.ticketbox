from ftw.upgrade import UpgradeStep


class MigrateDescriptionToTicketDescription(UpgradeStep):
    """Migrate description to ticket description.
    """

    def __call__(self):
        query = {'portal_type': 'Ticket'}
        for ticket in self.objects(query, 'Migrate Ticket description'):
            description = ticket.getRawDescription()
            ticket.Schema()['ticket_description'].set(ticket, description)
            ticket.setDescription('')
