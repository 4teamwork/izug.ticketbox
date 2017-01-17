from AccessControl import getSecurityManager
from Acquisition import aq_inner, aq_parent
from copy import deepcopy
from DateTime import DateTime
from izug.ticketbox.interfaces import ITicket, IResponseContainer, IResponse
from izug.ticketbox.interfaces import ITicketboxDatagridIdUpdater
from persistent import Persistent
from persistent.list import PersistentList
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.CMFCore.utils import getToolByName
from zope.annotation.interfaces import IAnnotations
from zope.app.component import hooks
from zope.app.component.hooks import getSite
from zope.app.container.contained import ObjectAddedEvent
from zope.app.container.contained import ObjectRemovedEvent
from zope.app.container.interfaces import UnaddableError
from zope.component import adapts
from zope.component import queryUtility
from zope.event import notify
from zope.interface import implements


class TicketboxDatagridIdUpdater(object):
    """A Ticketbox has a lot of datagrid fields to define different
    attributes dynamically (i.e. state, priorities...).

    For each datagrid-row we generate an id wich will be used
    to query the catalog and to reference in a ticket.

    If the user changes a title of a ticketbox datagrid row, we have
    to change the id too. Otherwise, orderings and groupings wont
    work properly again.

    We look for changes in the datagrid fields and updates the ids.
    If we have found changes, we update all tickets which where referenced
    with one of the changed ids.

    """

    implements(ITicketboxDatagridIdUpdater)

    ticketbox_ticket_field_mapping = {
        'availableStates': 'state',
        'availableReleases': 'releases',
        'availablePriorities': 'priority',
        'availableAreas': 'area',
        'availableVarieties': 'variety',
    }

    def __init__(self, context):
        self.context = context
        self.catalog = getToolByName(context, 'portal_catalog')

    def __call__(self):
        self.update()

    def update(self):
        """Search for changed rows in the ticketbox and updates the datagrid-ids
        and all its related tickets
        """

        # changed_fields contains all changed ids in the datagrid.
        #
        # The key is the ticketbox field name which contains changes.
        # The value is a list with tuples containing the old id as
        # the first entry and the new id as the new id
        #
        # ``changed_fields`` example:
        #
        # >>> {'availableAreas': [('my-Area', 'my-cool-area')],
        # ...  'availablePriorities': [('', 'high'), ('lower', 'low')],
        # ...  'availableStates': [('a-state', 'd-state')]}
        changed_fields = {}
        for field_name in self.ticketbox_ticket_field_mapping.keys():
            values = self.context.getField(field_name).get(self.context)
            changed_rows = self.uniquify_ids(values)
            if changed_rows:
                changed_fields[field_name] = changed_rows

        return self.update_tickets(changed_fields)

    def update_tickets(self, changed_fields={}):
        """Updates all ticket ids referencing to an old ticketbox
        datagrid id and reindexes modified tickets.
        """
        updated_tickets = []
        if not changed_fields:
            # Do nothing if nothing changed in the datagrid
            return updated_tickets

        for ticket in self.context.listFolderContents({'portal_type': 'Ticket'}):
            updated_fields = []

            # Iterate over all changed attributes
            for field_name, changes in changed_fields.items():

                # Do nothing if there where no changes for this attribute
                if not changes:
                    continue

                # Iterate over all changes for this attribute
                for old_id, new_id in changes:
                    if not old_id:
                        # This seems to be a new entry and there was no
                        # id generated yet. We don't have to do anything
                        continue

                    field = ticket.getField(
                        self.ticketbox_ticket_field_mapping.get(field_name))

                    current_id = field.get(ticket)

                    if old_id != current_id:
                        # Do not update the ticket if it is not related with
                        # a changed datagrid row.
                        continue

                    # Set the new id to the tickets field
                    field.set(ticket, new_id)

                    updated_fields.append(field)

            if updated_fields:
                updated_tickets.append(ticket)
                self.reindex_ticket(ticket, updated_fields)

        return updated_tickets

    def reindex_ticket(self, ticket, updated_fields):
        idxs = []
        for field in updated_fields:
            idxs.append(field.accessor)

        self.catalog.reindexObject(ticket, idxs=idxs)

    def uniquify_ids(self, data):
        """Creates unique ids within a list of dicts.
        Sets the "id" key of each dicts, creates the id with the value of
        "title" within the dict.

        ``data`` example:

        >>> [{'id': '', 'title': 'Foo'},
        ...  {'id': 'bar', 'title': 'Bar'}]

        if the ID is already set but the title changed, it will update
        the id with a newly generated one.

        example:

        >>> uniquify_ids([
        ...    {'id': 'foo', 'title': 'Chuck'},
               {'id': 'bar', 'title': 'Bar'}])

        >>> [{'id': 'chuck', 'title': 'Chuck'}, [{'id': 'bar', 'title': 'Bar'},

        if the title changed to an already existing title it will update to a
        new unique id:

        >>> uniquify_ids([
        ...    {'id': 'foo', 'title': 'Bar'},
               {'id': 'bar', 'title': 'Bar'}])

        >>> [{'id': 'bar-1', 'title': 'Bar'}, [{'id': 'bar', 'title': 'Bar'},


        if the title didn't change, it will do nothing.
        """
        existing_ids = set([item.get('id') for item in data if item.get('id')])
        changes = []
        for item in data:
            old_id = item.get('id')

            existing_ids_without_old_id = deepcopy(existing_ids)
            existing_ids_without_old_id.difference_update([old_id])

            new_id = self.create_uniqe_id(
                item.get('title'), existing_ids_without_old_id)

            if old_id == new_id:
                continue

            item['id'] = new_id
            existing_ids.add(new_id)

            changes.append((old_id, new_id))

        return changes

    def create_uniqe_id(self, title, existing_ids):
        """Creates a uniqe id by using the IIDNormalizer utility.
        """

        id_ = queryUtility(IIDNormalizer).normalize(title)

        if id_ not in existing_ids:
            return id_

        base_id = id_
        index = 0

        while id_ in existing_ids:
            index += 1
            id_ = '%s-%i' % (base_id, index)

        return id_


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
            individual_identifier = object_.getIndividualIdentifier()
            if individual_identifier:
                individual_identifier = ' [%s]' % individual_identifier
            subject = '%s%s %s' % (
                sheet.getProperty('notification_email_subject',
                                  default_subject),
                individual_identifier,
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
            individual_identifier = aq_parent(
                self.context).getIndividualIdentifier()
            if individual_identifier:
                individual_identifier = ' [%s]' % individual_identifier

            subject = '%s%s #%s - %s' % (
                sheet.getProperty('notification_email_subject',
                                  default_subject),
                individual_identifier,
                object_.getId(),
                object_.Title())

        return subject
