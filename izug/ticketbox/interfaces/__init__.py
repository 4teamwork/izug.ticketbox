# -*- extra stuff goes here -*-
from ticket import ITicket
from ticketbox import ITicketBox

__author__ = """Martin Aspeli <optilude@gmx.net>"""
__docformat__ = 'plaintext'


# Classes
import Issue
import Response

from zope.interface import Interface


class ITracker(Interface):
    """Marker interface for Poi issue tracker."""


class IIssue(Interface):
    """Marker interface for Poi issue.
    """
    pass


class IResponse(Interface):
    """Marker interface for Poi response.
    """
    pass
