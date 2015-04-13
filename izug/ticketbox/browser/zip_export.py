from ftw.zipexport.browser.available import ZipExportEnabled


class ZipExportDisabled(ZipExportEnabled):
    """
    This view can be used to hide the zip export action menu by overriding
    the view in the zcml for selected interfaces.
    """
    def zipexport_enabled(self):
        return False
