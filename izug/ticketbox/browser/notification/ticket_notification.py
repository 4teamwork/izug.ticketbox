from ftw.notification.email.templates.base import BaseEmailRepresentation
from izug.ticketbox import ticketboxMessageFactory as _
from izug.ticketbox.browser.helper import map_attribute, readable_author
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.i18nmessageid import Message
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner


class TicketEmailRepresentation(BaseEmailRepresentation):

    template = ViewPageTemplateFile('ticket.pt')

    def getTracker(self):
        context = self.context
        tracker = context.aq_parent

        return tracker

    def get_responses(self):
        base_response = self.context.restrictedTraverse('base_response')
        return base_response.responses()

    def creator(self):
        if self.infos()['response'] is True:
            responses = self.get_responses()
            response = responses[len(responses) - 1]
            userid = response['response'].creator
        else:
            context = aq_inner(self.context)
            userid = context.Creator()

        mem_tool = getToolByName(self.context, 'portal_membership')
        member = mem_tool.getMemberById(userid)
        return member.getUser().getProperty('fullname', userid)

    def infos(self):
        """Returns Infos for email-template"""
        responses = self.get_responses()
        author = readable_author(self.context)

        if isinstance(author, Message):
            author = self.context.translate(author)

        ticket_infos = {'tracker_title': self.context.aq_parent.title,
                        'tracker_url': self.context.aq_parent.absolute_url(),
                        'title': self.context.Title(),
                        'ticket_id': self.context.getId(),
                        'individualIdendifier':
                            self.context.aq_parent.getIndividualIdentifier,
                        'url': self.context.absolute_url(),
                        'text': self.context.getTicket_description(),
                        'state': map_attribute(self.context, "state"),
                        'responsibleManager': author,
                        'priority': map_attribute(self.context, "priority"),
                        'area': map_attribute(self.context, "area"),
                        'variety': map_attribute(self.context, "variety"),
                        'releases': map_attribute(self.context, "releases"),
                        'watchedRelease': map_attribute(self.context,
                                                        "watchedRelease"),
                        'answerDate': self.context.toLocalizedTime(
                            self.context.getAnswerDate(), long_format=True),
                        'response': False}
        if responses == []:
            return ticket_infos
        else:
            response_date = responses[len(responses) - 1]['response'].date
            if self.context.modification_date > response_date:
                return ticket_infos
            else:
                response = responses[len(responses) - 1]
                changes = {
                    'tracker_title': self.context.aq_parent.title,
                    'tracker_url': self.context.aq_parent.absolute_url(),
                    'title': self.context.Title(),
                    'ticket_id': self.context.getId(),
                    'individualIdendifier':
                        self.context.aq_parent.getIndividualIdentifier,
                    'url': self.context.absolute_url(),
                    'text': '',
                    'state': '',
                    'responsibleManager': '',
                    'priority': '',
                    'area': '',
                    'variety': '',
                    'releases': '',
                    'watchedRelease': '',
                    'answerDate': '',
                    'response': True}
                for item in response['response'].changes:
                    # XXX: Hack to solve the label_unassigned translations
                    # problem.
                    # If we retrieve a responsibleManager named
                    # label_unassigned, try to translate it
                    if item['id'] == 'responsibleManager':
                        if item['before'] == 'label_unassigned':
                            item['before'] = self.context.translate(
                                _(item['before']))
                        if item['after'] == 'label_unassigned':
                            item['after'] = self.context.translate(
                                _(item['after']))

                    changes[item['id']] = (
                        item['before'] + ' &rarr; ' + item['after'])
                changes['text'] = response['response'].text
                return changes
