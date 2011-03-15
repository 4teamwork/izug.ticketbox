from ftw.tabbedview.browser.views import views


class TabbedTicketBoxView(views.TabbedView):

    filter_state = True
    show_searchform = True

    def get_tabs(self):
        return [{'id':'Overview', 'class':''},
                {'id':'all_tickets', 'class':''},
                {'id':'my_tickets', 'class':''},
                {'id':'attachments', 'class':''},
                {'id':'info_view', 'class':''},
               ]
