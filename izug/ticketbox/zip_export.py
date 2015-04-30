from ftw.zipexport.interfaces import IZipRepresentation
from ftw.zipexport.representations.archetypes import FolderZipRepresentation
from ftw.zipexport.representations.general import NullZipRepresentation
from izug.ticketbox.export import get_header, get_data, create_xlsx
from izug.ticketbox.interfaces import ITicketBox, ITicket
from Products.CMFPlone.utils import safe_unicode
from StringIO import StringIO
from zope.component import adapts
from zope.interface import implements, Interface


class TicketBoxZipRepresentation(FolderZipRepresentation):
    implements(IZipRepresentation)
    adapts(ITicketBox, Interface)

    def get_files(self, path_prefix=u"", recursive=True, toplevel=True):
        """
        Returns a list of two-value-tuples having the following values:
        - a relative path under which the file should show up in the zip
        - the data as either a file or a stream
        """
        header = get_header(self.context)
        data = get_data(self.context)
        xlsx = create_xlsx(header, data)

        filename = '{0}.xlsx'.format(self.context.getId())

        yield (u'{0}/{1}'.format(safe_unicode(path_prefix),
                                 safe_unicode(filename)), xlsx)

        # Recursively export folder contents.
        folder_contents = super(TicketBoxZipRepresentation, self).get_files(
            path_prefix, recursive, toplevel)

        for item in folder_contents:
            yield item


class TicketZipRepresentation(NullZipRepresentation):
    implements(IZipRepresentation)
    adapts(ITicket, Interface)

    def get_files(self, path_prefix=u"", recursive=False, toplevel=True):
        attachments = self.context.getAttachments()

        # Put the attachments in a folder per ticket.
        path_prefix = u'{0}/{1}'.format(safe_unicode(path_prefix),
                                        safe_unicode(self.context.Title()))

        for attachment in attachments:
            filename = attachment.getFilename()
            yield (u'{0}/{1}'.format(safe_unicode(path_prefix),
                                     safe_unicode(filename)),
                   StringIO(attachment.data))
