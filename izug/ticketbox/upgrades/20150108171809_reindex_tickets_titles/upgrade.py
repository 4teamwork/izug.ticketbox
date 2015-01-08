from ftw.upgrade import UpgradeStep


class ReindexTicketsTitles(UpgradeStep):
    """Reindex the titles of the tickets.
    """

    def __call__(self):
        self.catalog_reindex_objects(
            query={'object_provides': 'izug.ticketbox.interfaces.ITicket'},
            idxs=['Title', 'sortable_title']
        )
