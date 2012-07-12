from Acquisition import aq_inner
from DateTime import DateTime
from izug.ticketbox import ticketboxMessageFactory as _
from izug.ticketbox.adapters import Response
from izug.ticketbox.browser.helper import map_attribute
from izug.ticketbox.config import DEFAULT_ISSUE_MIME_TYPE
from izug.ticketbox.interfaces import IResponseAdder
from izug.ticketbox.interfaces import IResponseContainer
from OFS.Image import File
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.memoize.view import memoize
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from zope.cachedescriptors.property import Lazy
from zope.component import getUtility
from zope.component import queryUtility
from zope.interface import implements
from zope.lifecycleevent import modified
from zope.schema.interfaces import IVocabularyFactory


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
        """Returns all Responses in the ticket
        """
        context = aq_inner(self.context)
        trans = context.portal_transforms
        items = []
        for id_, response in enumerate(self.folder):
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
            info = dict(id=id_,
                        response=response,
                        attachment=self.attachment_info(id_),
                        references=self.references_info(id_),
                        html=html)
            items.append(info)
        return items

    def get_years(self):
        """return a list of years in past and future"""

        years = []
        year = DateTime().year() - 3
        for _i in range(1, 10):
            years.append(year)
            year += 1

        return years

    @property
    @memoize
    def portal_url(self):
        context = aq_inner(self.context)
        plone = context.restrictedTraverse('@@plone_portal_state')
        return plone.portal_url()

    def attachment_info(self, id_):
        """Return TicketAttachment object
        """
        context = aq_inner(self.context)
        response = self.folder[id_]
        # Get attachment uid
        # In future this could be a list of attachments
        attachment_uid = response.attachment
        if attachment_uid is None:
            return None

        return context.reference_catalog.lookupObject(attachment_uid)

    def references_info(self, id_):
        """Return references of response"""
        context = aq_inner(self.context)
        response = self.folder[id_]

        # Fallback for old responses
        if not hasattr(response, 'references'):
            return []

        objs = []
        for uid in response.references:
            if uid:
                obj = context.reference_catalog.lookupObject(uid)
                if obj:
                    objs.append(obj)
        return objs

    def mock_reference_field(self):
        """Mocks reference field for response"""

        startuppath = '/'.join(self.context.getPhysicalPath())

        class Dummy(object):
            # Disable zope security
            __allow_access_to_unprotected_subobjects__ = True
            multiValued = 1
            # Use the same fieldname for our repsonse widet as we
            # use for the ticket reference (load some settings)
            getName = 'ticketReferences'

            class Widget(object):
                __allow_access_to_unprotected_subobjects__ = True
                allow_sorting = 0
                getStartupDirectory = lambda x, y, z: startuppath
            widget = Widget()

        return Dummy()

    @Lazy
    def memship(self):
        context = aq_inner(self.context)
        return getToolByName(context, 'portal_membership')

    @property
    @memoize
    def can_edit_response(self):
        context = aq_inner(self.context)
        return self.memship.checkPermission(
            'Modify portal content',
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
            msg = _(u"msg_no_response", default=u"No Response was selected")
            msg = self.context.translate(msg)
            status.addStatusMessage(msg, type='error')
            return -1
        else:
            try:
                response_id = int(response_id)
            except ValueError:
                msg = _(u"msg_nointeger",
                        default=u"Response id ${response_id} is no integer.",
                        mapping=dict(response_id=response_id))
                msg = self.context.translate(msg)
                status.addStatusMessage(msg, type='error')
                return -1
            if response_id >= len(self.folder):
                msg = _(
                    u"msg_invalid",
                    default=u"The Response ID ${response_id} doesn't exist.",
                    mapping=dict(response_id=response_id))
                msg = self.context.translate(msg)
                status.addStatusMessage(msg, type='error')
                return -1
            else:
                return response_id
        # fallback
        return -1

    @property
    def priority(self):
        context = aq_inner(self.context)
        return context.getPriority()

    @property
    def releases(self):
        context = aq_inner(self.context)
        return context.getReleases()

    @property
    def state(self):
        context = aq_inner(self.context)
        return context.getState()

    @property
    @memoize
    def states_for_display(self):
        factory = getUtility(IVocabularyFactory,
                             name='ticketbox_values_states')
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
    @memoize
    def varieties_for_display(self):
        context = aq_inner(self.context)
        result = []
        for term in context.getAvailableVarieties():
            current_state = self.context.getVariety()
            checked = term['id'] == current_state
            result.append(
                dict(
                    value=term['id'],
                    label=term['title'],
                    checked=checked))

        return result

    @property
    @memoize
    def available_varieties(self):
        """Get the available varieties for this issue.
        """
        return [t['value'] for t in self.varieties_for_display]

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
        factory = getUtility(
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
    def watched_releases_for_display(self):
        """Get the releases from the project.

        Usually nothing, unless you use Ticketbox in combination with
        PloneSoftwareCenter.
        """
        result = []
        factory = getUtility(
            IVocabularyFactory,
            name='ticketbox_values_releases')
        for term in factory(self.context.aq_inner):
            current_state = self.context.getWatchedRelease()
            checked = term.token == current_state
            result.append(
                dict(
                    value=term.token,
                    label=term.title,
                    checked=checked))
        return result

    @property
    @memoize
    def available_watched_releases(self):
        """Get the available watched releases for this issue.
        """
        return [t['value'] for t in self.watched_releases_for_display]

    @property
    def show_target_releases(self):
        """Should the option for selecting a target release be shown?

        There is always at least one option: None.  So only show when
        there is more than one option.
        """
        return len(self.available_releases) > 1

    @property
    def show_watched_releases(self):
        """Should the option for selecting a target release be shown?

        There is always at least one option: None.  So only show when
        there is more than one option.
        """
        return len(self.available_watched_releases) > 1

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
    def multiple_varieties(self):
        """Should the option for selecting a target variety be shown?

        There is always at least one option: None.  So only show when
        there is more than one option.
        """
        return len(self.varieties_for_display) > 1

    @property
    def managers_for_display(self):
        """Get the tracker managers.
        """
        context = self.context.aq_inner
        users = context.assignable_users()
        result = []
        assignedUser = context.getResponsibleManager()
        for user in users:
            result.append(dict(value=user[0],
                               label=user[1],
                               checked=assignedUser == user[0]))
        return result

    @property
    @memoize
    def available_managers(self):
        """Get the tracker managers.
        """
        # get vocab from issue
        result = []
        for user in self.context.aq_inner.assignable_users():
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
        modifiedDate = context.modified()
        response_text = form.get('response', u'')
        new_response = Response(response_text)
        new_response.mimetype = self.mimetype
        new_response.type = self.determine_response_type(new_response)

        issue_has_changed = False
        #Unassigned is no member in portal_membership.
        #So we have to set it manually
        unassigned = _(u'label_unassigned', default=u'unassigned')
        responsible_after = form.get('responsibleManager', u'')
        if responsible_after != context.getResponsibleManager():

            #get ResponsibleManager and member-infos before changes
            responsible_before = context.getResponsibleManager()
            member_before = self.context.portal_membership.getMemberById(
                responsible_before)

            context.setResponsibleManager(responsible_after)

            #get member-infos after changes
            member_after = self.context.portal_membership.getMemberById(
                responsible_after)

            #get fullname from member before changes
            if member_before:
                before = member_before.getProperty(
                    'fullname', responsible_before)
            else:
                before = unassigned

            #get fullname from member after changes
            if member_after:
                after = member_after.getProperty(
                    'fullname', responsible_after)
            else:
                after = unassigned

            new_response.add_change('responsibleManager',
                                    _(u'label_responsibleManager',
                                      default=u"Responsible"),
                                    before, after)
            issue_has_changed = True

        #Answerdate
        answerdate_after = form.get('answerdate')
        if answerdate_after:
            answerdate_after = DateTime(answerdate_after).strftime(
                '%d.%m.%Y %H:%M')
        answerdate_before = context.getAnswerDate()
        if answerdate_before:
            answerdate_before = answerdate_before.strftime('%d.%m.%Y %H:%M')
        else:
            answerdate_before = ''

        if answerdate_before != answerdate_after:
            context.setAnswerDate(answerdate_after)
            new_response.add_change('answerDate',
                                    _(u'label_answerdate',
                                      default=u'Answerdate'),
                                    answerdate_before,
                                    answerdate_after)
            issue_has_changed = True

        options = [
            ('priority',
             _(u'label_priority_', default=u"Priority"),
             'available_priorities'),

            ('releases',
             _(u'label_releases', default=u"Target Release"),
             'available_releases'),

            ('state',
             _(u'label_state', default=u"State"),
             'available_states'),

            ('area',
             _(u'label_areas', default=u"Area"),
             'available_areas'),

            ('variety',
             _(u'label_varieties', default=u"Variety"),
             'available_varieties'),

            ('watchedRelease',
             _(u'label_watched_release', default=u"Watched Release"),
             'available_watched_releases'),
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
                    new_response.add_change(
                        option, title,
                        map_attribute(self.context, option, current),
                        map_attribute(self.context, option, new))
                    issue_has_changed = True

        attachment = form.get('attachment')
        if attachment:
            # Create filename like AT - some Browser delivers the
            # local full path
            filename = attachment.filename
            filename = filename[max(
                    filename.rfind('/'),
                    filename.rfind('\\'),
                    filename.rfind(':')) + 1:]

            # File(id, title, file)
            data = File(filename, filename, attachment)
            if not hasattr(data, 'filename'):
                setattr(data, 'filename', filename)
            # Create TicketAttachment and save the uid in attachment attr of
            # new_response
            new_id = queryUtility(IIDNormalizer).normalize(
                filename.decode('utf-8'))
            if context.get(new_id, None):
                IStatusMessage(context.REQUEST).addStatusMessage(
                    _(u"text_file_exists_error"), type='error')
                context.setAttachment('DELETE_FILE')
                return self.request.response.redirect(context.absolute_url())
            new_file_id = context.invokeFactory(
                type_name="TicketAttachment",
                id=new_id,
                title=filename,
                file=data)
            new_file = context.get(new_file_id, None)
            new_response.attachment = new_file.UID()
            issue_has_changed = True

        references = form.get('ticketReferences')
        if references:
            new_response.references = references
            # Store refs also on Ticket
            self.context.setTicketReferences(
                references + self.context.getRawTicketReferences())

        if len(response_text) == 0 and not issue_has_changed:
            status = IStatusMessage(self.request)
            msg = _(
                u"msg_no_changes",
                default="No response text added and no issue changes made.")
            #
            # msg = self.context.translate(msg)
            status.addStatusMessage(msg, type='error')
        else:
            # Apply changes to issue
            # XXX: CHANGE WORKFLOW - OR CHANGE SECURITYMANAGER
            # We cannot use AT's update method, because of a security check
            # we don't want. Let's set the new values manually.
            # OLD:
            # context.update(**changes)

            # NEW:
            if 'releases' in changes:
                context.setReleases(changes['releases'])
            if 'priority' in changes:
                context.setPriority(changes['priority'])
            if 'area' in changes:
                context.setArea(changes['area'])
            if 'variety' in changes:
                context.setVariety(changes['variety'])
            if 'state' in changes:
                context.setState(changes['state'])
            if 'watchedRelease' in changes:
                context.setWatchedRelease(changes['watchedRelease'])

            # Add response
            catalog_tool = self.context.portal_catalog
            # re-set the modification date -
            # this must be the last modifying access
            context.reindexObject()
            self.folder.add(new_response)
            context.setModificationDate(modifiedDate)
            catalog_tool.catalog_object(context,
                                        '/'.join(context.getPhysicalPath()))
        if form.get('sendNotification', None):
            self.request.response.redirect(
                context.absolute_url() + '/notification_form')
        else:
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

        response_id = form.get('response_id', None)
        if response_id is None:
            msg = _(u"msg_no_response_selected",
                    default=u"No response selected for saving.")
            msg = self.context.translate(msg)
            status.addStatusMessage(msg, type='error')
        elif self.folder[response_id] is None:
            msg = _(u"msg_doesnt_exists",
                    default=u"Response does not exist anymore; \
                    perhaps it was removed by another user.")
            msg = self.context.translate(msg)
            status.addStatusMessage(msg, type='error')

        response = self.folder[response_id]

        member = context.portal_membership.getAuthenticatedMember()
        if not (self.can_edit_response or response.creator == member.getId()):
            msg = _(u"msg_not_restricted",
                    default=u"You are not allowed to edit responses.")
            msg = self.context.translate(msg)
            status.addStatusMessage(msg, type='error')
        else:
            response_text = form.get('response', u'')
            response.text = response_text
            # Remove cached rendered response.
            response.rendered_text = None
            msg = _(u"msg_changes_saved", default="Changes Saved",
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
            msg = _(u"msg_restricted_delete",
                    default=u"You are not allowed to delete Responses")
            msg = self.context.translate(msg)
            status.addStatusMessage(msg, type='error')
        else:
            response_id = self.request.form.get('response_id', None)
            if response_id is None:
                msg = _(u"msg_no_response_delete",
                        default=u"No response selected for removal.")
                msg = self.context.translate(msg)
                status.addStatusMessage(msg, type='error')
            else:
                try:
                    response_id = int(response_id)
                except ValueError:
                    msg = _(
                        u"msg_nointeger",
                        default=u"Response id ${response_id} is no integer.",
                        mapping=dict(response_id=response_id))
                    msg = self.context.translate(msg)
                    status.addStatusMessage(msg, type='error')
                    self.request.response.redirect(context.absolute_url())
                    return

                if response_id >= len(self.folder):
                    msg = _(u"msg_invalid",
                            default=u"The Response ID ${response_id} "
                            "doesn't exist.",
                            mapping=dict(response_id=response_id))
                    msg = self.context.translate(msg)
                    status.addStatusMessage(msg, type='error')
                else:
                    self.folder.delete(response_id)
                    msg = _(u"msg_removed", default="Removed response.",
                            mapping=dict(response_id=response_id))
                    msg = self.context.translate(msg)
                    status.addStatusMessage(msg, type='info')
        self.request.response.redirect(context.absolute_url())
