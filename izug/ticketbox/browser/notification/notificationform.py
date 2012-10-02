from ftw.notification.base.browser.views import NotificationForm as base


class NotificationForm(base):
    """Notification with preselect for tickets"""

    def __init__(self, context, request):
        super(NotificationForm, self).__init__(context, request)
        self.pre_select = []

        self.pre_select.append(self.context.getResponsibleManager())

