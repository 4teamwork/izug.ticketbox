from AccessControl import ClassSecurityInfo
from izug.ticketbox.config import PROJECTNAME
from izug.ticketbox.interfaces import IAttachment
from Products.Archetypes import atapi
from Products.Archetypes.BaseContent import BaseContent
from Products.ATContentTypes.config import ICONMAP
from Products.ATContentTypes.content.file import ATFile
from Products.CMFCore.utils import getToolByName
from Products.MimetypesRegistry.common import MimeTypeException
from urllib import quote
from zope.interface import implements
import logging


class TicketAttachment(ATFile):
    """A file content type based on blobs.
    """
    implements(IAttachment)
    security = ClassSecurityInfo()

    security.declarePublic('getIcon')
    def getIcon(self, relative_to_portal=0):
        """Calculate the icon using the mime type of the file
        """

        field = self.getField('file')
        if not field or not self.get_size():
            # field is empty
            return BaseContent.getIcon(self, relative_to_portal)

        contenttype = field.getContentType(self)
        contenttype_major = contenttype and contenttype.split('/')[0] or ''

        mtr = getToolByName(self, 'mimetypes_registry', None)
        utool = getToolByName(self, 'portal_url')

        mimetypeitem = None
        try:
            mimetypeitem = mtr.lookup(contenttype)
        except MimeTypeException, msg:
            LOG = logging.getLogger('ATCT')
            LOG.error('MimeTypeException for {0}. Error is: {1}'.format(
                self.absolute_url(),
                str(msg)))
        if not mimetypeitem:
            icon = None
        else:
            icon = mimetypeitem[0].icon_path

        if not icon:
            if contenttype in ICONMAP:
                icon = quote(ICONMAP[contenttype])
            elif contenttype_major in ICONMAP:
                icon = quote(ICONMAP[contenttype_major])
            else:
                return BaseContent.getIcon(self, relative_to_portal)

        if relative_to_portal:
            return icon
        else:
            # Relative to REQUEST['BASEPATH1']
            res = utool(relative=1) + '/' + icon
            while res[:1] == '/':
                res = res[1:]
            return res

atapi.registerType(TicketAttachment, PROJECTNAME)
