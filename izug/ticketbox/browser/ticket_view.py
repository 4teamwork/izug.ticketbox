from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class TicketView(BrowserView):

    template = ViewPageTemplateFile('ticket_view.pt')

    def getResponses(self):
        """lkasdj"""
        return 'test'

    def getAttachments(self):
        """alsjd"""
        att = self.context.getAttachment()
        url = att.absolute_url()
        render_att= '<a href="'+ url+'"><img src="'+att.portal_url()+'/'+att.getIcon()+'" /></a>'
        render_att=render_att + '<a href="' + url+'">'+att.filename+'</a>'
        return render_att
