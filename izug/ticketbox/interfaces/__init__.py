from ticket import ITicket
from ticketbox import ITicketBox

__author__ = """Martin Aspeli <optilude@gmx.net>"""
__docformat__ = 'plaintext'


# Classes
import Issue
import Response

from zope.interface import Interface


class IResponse(Interface):
    """Marker interface for TicketBox response.
    """
    pass
