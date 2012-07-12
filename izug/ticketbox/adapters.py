from AccessControl import getSecurityManager
from DateTime import DateTime
from izug.ticketbox.interfaces import ITicket, IResponseContainer, IResponse
from persistent import Persistent
from persistent.list import PersistentList
from zope.annotation.interfaces import IAnnotations
from zope.app.container.contained import ObjectAddedEvent
from zope.app.container.contained import ObjectRemovedEvent
from zope.app.container.interfaces import UnaddableError
from zope.component import adapts
from zope.event import notify
from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from zope.app.component import hooks
from Acquisition import aq_inner, aq_parent
from zope.app.component.hooks import getSite


class ResponseContainer(Persistent):

    implements(IResponseContainer)
    adapts(ITicket)
    ANNO_KEY = 'izug.ticketbox.responses'

    def __init__(self, context):
        self.context = context
        annotations = IAnnotations(self.context)
        self.__mapping = annotations.get(self.ANNO_KEY, None)
        if self.__mapping is None:
            self.__mapping = PersistentList()
            annotations[self.ANNO_KEY] = self.__mapping

    def __contains__(self, key):
        '''See interface IReadContainer

        Taken from zope.app.container.btree.

        Reimplement this method, since has_key() returns the key if available,
        while we expect True or False.

        >>> c = ResponseContainer()
        >>> "a" in c
        False
        >>> c["a"] = 1
        >>> "a" in c
        True
        >>> "A" in c
        False
        '''
        return key in self.__mapping

    has_key = __contains__

    def __getitem__(self, i):
        i = int(i)
        return self.__mapping.__getitem__(i)

    def __delitem__(self, item):
        self.__mapping.__delitem__(item)

    def __len__(self):
        return self.__mapping.__len__()

    def __setitem__(self, i, y):
        self.__mapping.__setitem__(i, y)

    def append(self, item):
        self.__mapping.append(item)

    def remove(self, id_):
        """Remove item 'id_' from the list.

        We don't actually remove the item, we just set it to None,
        so that when you edit item 3 out of 3 and someone deletes
        item 2 you are not left in the water.

        Note that we used to get passed a complete item, not an id.
        """
        id_ = int(id_)
        self[id_] = None

    def add(self, item):
        if not IResponse.providedBy(item):
            raise UnaddableError(self, item,
                                 "IResponse interface not provided.")
        self.append(item)
        id_ = str(len(self))
        event = ObjectAddedEvent(item, newParent=self.context, newName=id_)
        notify(event)

    def delete(self, id_):
        # We need to fire an ObjectRemovedEvent ourselves here because
        # self[id_].__parent__ is not exactly the same as self, which
        # in the end means that __delitem__ does not fire an
        # ObjectRemovedEvent for us.
        #
        # Also, now we can say the oldParent is the issue instead of
        # this adapter.
        event = ObjectRemovedEvent(self[id_], oldParent=self.context,
                                   oldName=id_)
        self.remove(id_)
        notify(event)


class Response(Persistent):

    implements(IResponse)

    def __init__(self, text):
        self.__parent__ = self.__name__ = None
        self.text = text
        self.changes = PersistentList()
        sm = getSecurityManager()
        user = sm.getUser()
        self.creator = user.getId() or '(anonymous)'
        self.date = DateTime()
        self.type = 'additional'
        self.mimetype = ''
        self.rendered_text = None
        self.attachment = None
        self.references = []

    def add_change(self, id_, name, before, after):
        """Add a new issue change.
        """
        delta = dict(
            id=id_,
            name=name,
            before=before,
            after=after)
        self.changes.append(delta)

    def creator_fullname(self):
        site = getSite()
        member = site.portal_membership.getMemberById(self.creator)
        # In case of Creator no longer exists
        if member is None:
            return self.creator
        fullname = member.getProperty('fullname', member.getId())
        if fullname:
            return fullname
        return member.getId()


class EmptyExporter(object):

    def __init__(self, context):
        self.context = context

    def export(self, export_context, subdir, root=False):
        return


class TicketBoxSubjectCreator(object):

    def __init__(self, context):
        self.context = aq_inner(context)
        self.request = self.context.REQUEST

    def __call__(self, object_):
        site = hooks.getSite()
        portal_properties = getToolByName(object_, 'portal_properties')
        default_subject = '[%s] Notification:' % (site.Title())
        subject = None
        try:
            sheet = portal_properties['ftw.notification-properties']

        except AttributeError:
            subject = default_subject

        else:
            subject = '%s [%s] %s' % (
                sheet.getProperty('notification_email_subject',
                                  default_subject),
                object_.getIndividualIdentifier(),
                object_.Title())

        return subject


class TicketSubjectCreator(object):

    def __init__(self, context):
        self.context = aq_inner(context)
        self.request = self.context.REQUEST

    def __call__(self, object_):
        site = hooks.getSite()
        portal_properties = getToolByName(object_, 'portal_properties')
        default_subject = '[%s] Notification:' % (site.Title())
        subject = None
        try:
            sheet = portal_properties['ftw.notification-properties']
        except AttributeError:
            subject = default_subject

        else:
            subject = '%s [%s] #%s - %s' % (
                sheet.getProperty('notification_email_subject',
                                  default_subject),
                aq_parent(self.context).getIndividualIdentifier(),
                object_.getId(),
                object_.Title())

        return subject
