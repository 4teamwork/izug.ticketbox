from Products.CMFCore.utils import getToolByName
from izug.ticketbox.browser.interfaces import IResponseAdder
from zope.interface import implements
from zope.cachedescriptors.property import Lazy
from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from izug.ticketbox.adapters import IResponseContainer
from izug.ticketbox.adapters import Response
from plone.memoize.view import memoize
from izug.ticketbox.config import DEFAULT_ISSUE_MIME_TYPE
from izug.ticketbox import ticketboxMessageFactory as _
from Products.statusmessages.interfaces import IStatusMessage
from zope.lifecycleevent import modified
from OFS.Image import File
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from plone.i18n.normalizer import IDNormalizer
from izug.ticketbox.browser.helper import map_attribute

class Base(BrowserView):
    """Base view for Ticketbox Response.

    Mostly meant as helper for adding a Ticketbox Response.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.folder = IResponseContainer(context)
        self.mimetype = DEFAULT_ISSUE_MIME_TYPE
        self.use_wysiwyg = (self.mimetype == 'text/html')

    def responses(self):
        context = aq_inner(self.context)
        trans = context.portal_transforms
        items = []
        for id, response in enumerate(self.folder):
            if response is None:
                # Has been removed.
                continue
            # Use the already rendered response when available
            if response.rendered_text is None:
                if response.mimetype == 'text/html':
                    html = response.text
                else:
                    html = trans.convertTo('text/html',
                                           response.text,
                                           mimetype=response.mimetype)
                    html = html.getData()
                response.rendered_text = html
            html = response.rendered_text
            info = dict(id=id,
                        response=response,
                        attachment=self.attachment_info(id),
                        html=html)
            items.append(info)
        return items

    @property
    @memoize
    def portal_url(self):
        context = aq_inner(self.context)
        plone = context.restrictedTraverse('@@plone_portal_state')
        return plone.portal_url()

    def attachment_info(self, id):
        """Return TicketAttachment object
        """
        context = aq_inner(self.context)
        response = self.folder[id]
        # Get attachment uid
        # In future this could be a list of attachments
        attachment_uid = response.attachment
        if attachment_uid is None:
            return None

        return context.reference_catalog.lookupObject(attachment_uid)

    @Lazy
    def memship(self):
        context = aq_inner(self.context)
        return getToolByName(context, 'portal_membership')

    @property
    @memoize
    def can_edit_response(self):
        context = aq_inner(self.context)
        return self.memship.checkPermission(
            'izug.ticketbox: Add Ticket',
            context)

    @property
    @memoize
    def can_delete_response(self):
        context = aq_inner(self.context)
        return self.memship.checkPermission('Delete objects', context)

    def validate_response_id(self):
        """Validate the response id from the request.

        Return -1 if for example the response id does not exist.
        Return the response id otherwise.

        Side effect: an informative status message is set.
        """
        status = IStatusMessage(self.request)
        response_id = self.request.form.get('response_id', None)
        if response_id is None:
            msg = _(u"No response selected.")
            msg = self.context.translate(msg)
            status.addStatusMessage(msg, type='error')
            return -1
        else:
            try:
                response_id = int(response_id)
            except ValueError:
                msg = _(u"Response id ${response_id} is no integer.",
                        mapping=dict(response_id=response_id))
                msg = self.context.translate(msg)
                status.addStatusMessage(msg, type='error')
                return -1
            if response_id >= len(self.folder):
                msg = _(u"Response id ${response_id} does not exist.",
                        mapping=dict(response_id=response_id))
                msg = self.context.translate(msg)
                status.addStatusMessage(msg, type='error')
                return -1
            else:
                return response_id
        # fallback
        return -1

    @property
    def Priority(self):
        context = aq_inner(self.context)
        return context.getPriority()

    @property
    def Release(self):
        context = aq_inner(self.context)
        return context.getReleases()

    @property
    def State(self):
        context = aq_inner(self.context)
        return context.getState()



    @property
    @memoize
    def states_for_display(self):
        factory=getUtility(IVocabularyFactory, name='ticketbox_values_states')
        result = []
        for term in factory(self.context.aq_inner):
            current_state = self.context.getState()
            checked = term.token == current_state
            result.append(
                dict(
                    value=term.token,
                    label=term.title,
                    checked=checked))
        return result

    @property
    def available_states(self):
        return [t['value'] for t in self.states_for_display]


    @property
    def priorities_for_display(self):
        context = self.context.aq_inner
        result = []
        for term in context.getAvailablePriorities():
            current_state = self.context.getPriority()
            checked = term['id'] == current_state
            result.append(
                dict(
                    value=term['id'],
                    label=term['title'],
                    checked=checked))

        return result

    @property
    def areas_for_display(self):
        context = self.context.aq_inner
        result = []
        for term in context.getAvailableAreas():
            current_state = self.context.getArea()
            checked = term['id'] == current_state
            result.append(
                dict(
                    value=term['id'],
                    label=term['title'],
                    checked=checked))

        return result

    @property
    @memoize
    def available_areas(self):
        """Get the available severities for this issue.
        """
        return [t['value'] for t in self.areas_for_display]

    @property
    def responsibleManager(self):
        context = aq_inner(self.context)
        return context.getResponsibleManager()

    @property
    @memoize
    def available_priorities(self):
        """Get the available severities for this issue.
        """
        return [t['value'] for t in self.priorities_for_display]

    @property
    def releases_for_display(self):
        """Get the releases from the project.

        Usually nothing, unless you use Ticketbox in combination with
        PloneSoftwareCenter.
        """
        result = []
        factory=getUtility(
            IVocabularyFactory,
            name='ticketbox_values_releases')
        for term in factory(self.context.aq_inner):
            current_state = self.context.getReleases()
            checked = term.token == current_state
            result.append(
                dict(
                    value=term.token,
                    label=term.title,
                    checked=checked))
        return result

    @property
    @memoize
    def available_releases(self):
        """Get the releases from the project.
        """

        return [t['value'] for t in self.releases_for_display]

    @property
    def show_target_releases(self):
        """Should the option for selecting a target release be shown?

        There is always at least one option: None.  So only show when
        there is more than one option.
        """
        return len(self.available_releases) > 1

    @property
    def multiple_priorities(self):
        """Should the option for selecting a target release be shown?

        There is always at least one option: None.  So only show when
        there is more than one option.
        """
        return len(self.context.getAvailablePriorities()) > 1

    @property
    def multiple_states(self):
        """Should the option for selecting a target release be shown?

        There is always at least one option: None.  So only show when
        there is more than one option.
        """
        return len(self.states_for_display) > 1

    @property
    def multiple_areas(self):
        """Should the option for selecting a target area be shown?

        There is always at least one option: None.  So only show when
        there is more than one option.
        """
        return len(self.areas_for_display) > 1


    @property
    def managers_for_display(self):
        """Get the tracker managers.
        """
        context = self.context.aq_inner
        users=context.get_assignable_users()
        result = []
        assignedUser = context.getResponsibleManager()
        for user in users:
            result.append(dict(value=user[0],
                                label=user[1],
                                checked=assignedUser==user[0]))
        return result

    @property
    @memoize
    def available_managers(self):
        """Get the tracker managers.
        """
        # get vocab from issue
        result = []
        for user in self.context.aq_inner.get_assignable_users():
            result.append(user[0])
        return result

    @property
    @memoize
    def upload_allowed(self):
        """Is the user allowed to upload on attachment?
        """
        return True


class AddForm(Base):
    implements(IResponseAdder)

    def __init__(self, context, request, view):
        super(AddForm, self).__init__(context, request)
        self.__parent__ = view

    def update(self):
        pass

    def render(self):
        # self.template is defined in zcml
        return self.template()


class Create(Base):

    def determine_response_type(self, response):
        """Return a string indicating the type of response this is.
        """
        responseCreator = response.creator
        if responseCreator == '(anonymous)':
            return 'additional'

        issue = aq_inner(self.context)
        if responseCreator == issue.Creator():
            return 'clarification'

        if responseCreator in self.available_managers:
            return 'reply'

        # default:
        return 'additional'

    def __call__(self):
        form = self.request.form
        context = aq_inner(self.context)

        response_text = form.get('response', u'')
        new_response = Response(response_text)
        new_response.mimetype = self.mimetype
        new_response.type = self.determine_response_type(new_response)

        issue_has_changed = False
        responsibleManager = form.get('responsibleManager', u'')
        if responsibleManager != context.getResponsibleManager():
            before = context.getResponsibleManager()
            # Save new state on ticket
            context.setResponsibleManager(responsibleManager)
            member = self.context.portal_membership.getMemberById(responsibleManager)
            if member:
                after = member.getProperty('fullname', responsibleManager)
            new_response.add_change('responsibleManager', _(u'Issue state'),
                                    before, after)
            issue_has_changed = True

        options = [
            ('Priority', _(u'Priority'), 'available_priorities'),
            #('responsibleManager', _(u'Responsible manager'), 'available_managers'),
            ('Releases', _(u'Target release'), 'available_releases'),
            ('State', _(u'States'), 'available_states'),
            ('Area', _(u'Areas'), 'available_areas'),
            ]
        # Changes that need to be applied to the issue (apart from
        # workflow changes that need to be handled separately).
        changes = {}
        for option, title, vocab in options:
            new = form.get(option, u'')
            if new and new in self.__getattribute__(vocab):
                current = context.__getattribute__(option)
                if current != new:
                    changes[option] = new

                    new_response.add_change(option, title,
                                            map_attribute(self.context, option, current),
                                            map_attribute(self.context, option, new))
                    issue_has_changed = True


        attachment = form.get('attachment')
        if attachment:
            # File(id, title, file)
            data = File(attachment.filename, attachment.filename, attachment)
            if not hasattr(data, 'filename'):
                setattr(data, 'filename', attachment.filename)
            # Create TicketAttachment and save the uid in attachment attr of
            # new_response
            new_id = IDNormalizer.normalize(
                IDNormalizer(),
                attachment.filename)
            new_file_id = context.invokeFactory(
                type_name="TicketAttachment",
                id=new_id,
                title=attachment.filename,
                file=data)
            new_file = context.get(new_file_id, None)

            new_response.attachment = new_file.UID()
            issue_has_changed = True

        if len(response_text) == 0 and not issue_has_changed:
            status = IStatusMessage(self.request)
            msg = _(u"No response text added and no issue changes made.")
            #
            # msg = self.context.translate(msg)
            status.addStatusMessage(msg, type='error')
        else:
            # Apply changes to issue
            context.update(**changes)
            # Add response
            self.folder.add(new_response)
            self.context.reindexObject()
        self.request.response.redirect(context.absolute_url())


class Edit(Base):

    @property
    @memoize
    def response(self):
        form = self.request.form
        response_id = form.get('response_id', None)
        if response_id is None:
            return None
        try:
            response_id = int(response_id)
        except ValueError:
            return None
        if response_id >= len(self.folder):
            return None
        return self.folder[response_id]

    @property
    def response_found(self):
        return self.response is not None


class Save(Base):

    def __call__(self):
        form = self.request.form
        context = aq_inner(self.context)
        status = IStatusMessage(self.request)
        if not self.can_edit_response:
            msg = _(u"You are not allowed to edit responses.")
            msg = self.context.translate(msg)
            status.addStatusMessage(msg, type='error')
        else:
            response_id = form.get('response_id', None)
            if response_id is None:
                msg = _(u"No response selected for saving.")
                msg = self.context.translate(msg)
                status.addStatusMessage(msg, type='error')
            elif self.folder[response_id] is None:
                msg = _(u"Response does not exist anymore; perhaps it was "
                        "removed by another user.")
                msg = self.context.translate(msg)
                status.addStatusMessage(msg, type='error')
            else:
                response = self.folder[response_id]
                response_text = form.get('response', u'')
                response.text = response_text
                # Remove cached rendered response.
                response.rendered_text = None
                msg = _(u"Changes saved to response.",
                      mapping=dict(response_id=response_id))
                msg = self.context.translate(msg)
                status.addStatusMessage(msg, type='info')
                # Fire event.  We put the context in the descriptions
                # so event handlers can use this fully acquisition
                # wrapped object to do their thing.  Feels like
                # cheating, but it gets the job done.  Arguably we
                # could turn the two arguments around and signal that
                # the issue has changed, with the response in the
                # event descriptions.
                modified(response, context)
        self.request.response.redirect(context.absolute_url())


class Delete(Base):

    def __call__(self):
        context = aq_inner(self.context)
        status = IStatusMessage(self.request)

        if not self.can_delete_response:
            msg = _(u"You are not allowed to delete responses.")
            msg = self.context.translate(msg)
            status.addStatusMessage(msg, type='error')
        else:
            response_id = self.request.form.get('response_id', None)
            if response_id is None:
                msg = _(u"No response selected for removal.")
                msg = self.context.translate(msg)
                status.addStatusMessage(msg, type='error')
            else:
                try:
                    response_id = int(response_id)
                except ValueError:
                    msg = _(u"Response id ${response_id} is no integer so it "
                            "cannot be removed.",
                            mapping=dict(response_id=response_id))
                    msg = self.context.translate(msg)
                    status.addStatusMessage(msg, type='error')
                    self.request.response.redirect(context.absolute_url())
                    return
                if response_id >= len(self.folder):
                    msg = _(u"Response id ${response_id} does not exist so it "
                            "cannot be removed.",
                            mapping=dict(response_id=response_id))
                    msg = self.context.translate(msg)
                    status.addStatusMessage(msg, type='error')
                else:
                    self.folder.delete(response_id)
                    msg = _(u"Removed response.",
                            mapping=dict(response_id=response_id))
                    msg = self.context.translate(msg)
                    status.addStatusMessage(msg, type='info')
        self.request.response.redirect(context.absolute_url())
