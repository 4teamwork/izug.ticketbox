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