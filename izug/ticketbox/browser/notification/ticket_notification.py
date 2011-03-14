from ftw.notification.email.templates.base import BaseEmailRepresentation
from zope.app.pagetemplate import ViewPageTemplateFile


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
        ticket_infos = {'tracker_title': self.context.aq_parent.title,
                    'tracker_url': self.context.aq_parent.absolute_url(),
                    'title': self.context.Title(),
                    'url': self.context.absolute_url(),
                    'text': self.context.Description(),
                    'State': self.context.getState(),
                    'responsibleManager': self.context.getResponsibleManager(),
                    'Priority': self.context.getPriority(),
                    'Area': self.context.getArea(),
                    'Releases': self.context.getReleases(),
                    'response': False}
        if responses == []:
            return ticket_infos
        else:
            response_date = responses[len(responses)-1]['response'].date
            if self.context.modification_date > response_date:
                return ticket_infos
            else:
                response = responses[len(responses)-1]
                changes = {'tracker_title': self.context.aq_parent.title,
                           'tracker_url': self.context.aq_parent.absolute_url(),
                           'title':self.context.Title(),
                           'url':self.context.absolute_url(),
                           'text':'',
                           'State':'',
                           'responsibleManager':'',
                           'Priority':'',
                           'Area':'',
                           'Releases':'',
                           'response':True}
                for item in response['response'].changes:
                    changes[item['id']] = item['before'] + 	' &rarr; ' + item['after']
                changes['text'] = response['response'].text
                return changes
