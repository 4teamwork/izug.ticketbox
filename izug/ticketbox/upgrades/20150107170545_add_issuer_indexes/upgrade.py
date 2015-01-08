from ftw.upgrade import UpgradeStep


class AddIssuerIndexes(UpgradeStep):
    """Add issuer indexes.
    """

    def __call__(self):
        self.install_upgrade_profile()

        indexes = ['getIssuer', 'sortable_issuer']

        for index in indexes:
            self.catalog_add_index(index, 'FieldIndex')

        self.catalog_reindex_objects(
            query={'object_provides': 'izug.ticketbox.interfaces.ITicket'},
            idxs=indexes
        )
