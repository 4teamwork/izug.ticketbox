# pylint: disable=E0211, E0213
# E0211: Method has no argument
# E0213: Method should have "self" as first argument


from zope.contentprovider.interfaces import ITALNamespaceData
from zope.interface import Attribute
from zope.interface import directlyProvides
from zope.interface import Interface
from zope.viewlet.interfaces import IViewletManager


class ITicketBox(Interface):
    """A tracker-like task management system"""


class ITicket(Interface):
    """A ticket for the Ticketbox"""


class IResponseContainer(Interface):
    """holds the responses for a ticket"""
    pass


class IResponse(Interface):
    """A response for a ticket in the Ticketbox"""

    text = Attribute("Text of this response")
    rendered_text = Attribute("Rendered text (html) for caching")
    changes = Attribute("Changes made to the issue in this response.")
    creator = Attribute("Id of user making this change.")
    date = Attribute("Date (plus time) this response was made.")
    type = Attribute("Type of response (additional/clarification/reply).")
    mimetype = Attribute("Mime type of the response.")
    attachment = Attribute("File attachment.")

    def add_change(id_, name, before, after):
        """Add change to the list of changes.
        """


class ICreateResponse(Interface):
    """Create a response"""
    pass


class ITicketFolderView(Interface):
    """Abstract a Ticketbox into a folder for tickets.
    """

    def getFilteredIssues(criteria, **kwargs):
        """Get the contained issues in the given criteria.
        """

    def getIssueSearchQueryString(criteria, **kwargs):
        """Return a query string for an issue query.
        """

    def buildIssueSearchQuery(criteria, **kwargs):
        """Build canonical query for issue search.
        """

    def getMyIssues(openStates, memberId, manager):
        """Get a catalog query result set of my issues.

        So: all issues assigned to or submitted by the current user,
        with review state in openStates.

        If manager is True, you can add more states.
        """

    def getOrphanedIssues(openStates, memberId):
        """Get a catalog query result set of orphaned issues.

        Meaning: all open issues not assigned to anyone and not owned
        by the given user.
        """


class IResponseAdder(IViewletManager):

    mimetype = Attribute("Mime type for response.")
    use_wysiwyg = Attribute("Boolean: Use kupu-like editor.")

    def states_for_display():
        """Get the available transitions for this issue.
        """

    def severities_for_display():
        """Get the available severities for this issue.
        """

    def releases_for_display():
        """Get the releases from the project.
        """

    def managers_for_display():
        """Get the tracker managers.
        """

directlyProvides(IResponseAdder, ITALNamespaceData)
