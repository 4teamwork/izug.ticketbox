from ftw.notification.email.templates.base import BaseEmailRepresentation
from zope.app.pagetemplate import ViewPageTemplateFile
from izug.ticketbox.browser.helper import map_attribute, readable_author
from izug.ticketbox import ticketboxMessageFactory as _
from Products.CMFCore.utils import getToolByName


class TicketEmailRepresentation(BaseEmailRepresentation):

    template = ViewPageTemplateFile('ticket.pt')

    def getTracker(self):
        context = self.context
        tracker = context.aq_parent

        return tracker

    def creator(self):
        context = self.context.aq_inner
        return context.Creator()

    def infos(self):
        """Returns Infos for email-template"""
        base_response = self.context.restrictedTraverse('base_response')
        responses = base_response.responses()
        author = self.context.translate(readable_author(self.context))

        ticket_infos = {
                    'comment': self.request.form['comment'],
                    'tracker_title': self.context.aq_parent.title,
                    'tracker_url': self.context.aq_parent.absolute_url(),
                    'title': self.context.Title(),
                    'ticket_id': self.context.getId(),
                    'individualIdendifier':
                    self.context.aq_parent.getIndividualIdentifier,
                    'url': self.context.absolute_url(),
                    'text': self.context.Description(),
                    'state': map_attribute(self.context, "state"),
                    'responsibleManager': author,
                    'priority': map_attribute(self.context, "priority"),
                    'area': map_attribute(self.context, "area"),
                    'releases': map_attribute(self.context, "releases"),
                    'answerDate':self.context.getAnswerDate(),
                    'response': False}
        if responses == []:
            return ticket_infos
        else:
            response_date = responses[len(responses)-1]['response'].date
            if self.context.modification_date > response_date:
                return ticket_infos
            else:
                response = responses[len(responses)-1]
                changes = {
                    'comment': self.request.form['comment'],
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
                    'releases': '',
                    'answerDate':'',
                    'response': True}
                for item in response['response'].changes:
                    # XXX: Hack to solve the label_unassigned translations problem
                    # If we retrieve a responsibleManager named label_unassigned,
                    # try to translate it
                    if item['id'] == 'responsibleManager':
                        if item['before'] == 'label_unassigned':
                            item['before'] = self.context.translate(_(item['before']))
                        if item['after'] == 'label_unassigned':
                            item['after'] = self.context.translate(_(item['after']))

                    changes[item['id']] = (
                        item['before'] + 	' &rarr; ' + item['after'])
                changes['text'] = response['response'].text
                response_creator = response['response'].creator
                mt = getToolByName(self.context, 'portal_membership')
                member = mt.getMemberById(response_creator)
                if member:
                    response_creator = member.getProperty('fullname', response_creator)
                changes['response_creator'] = response_creator
                return changes
