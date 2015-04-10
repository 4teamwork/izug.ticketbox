from ftw.zipexport.interfaces import IZipRepresentation
from ftw.zipexport.representations.general import NullZipRepresentation
from izug.ticketbox.export import get_header, get_data, create_xlsx
from izug.ticketbox.interfaces import ITicketBox
from zope.component import adapts
from zope.interface import implements, Interface


class TicketBoxZipRepresentation(NullZipRepresentation):
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

        filename = u'{0}.xlsx'.format(self.context.getId())

        yield (u'{0}/{1}'.format(path_prefix, filename), xlsx)
