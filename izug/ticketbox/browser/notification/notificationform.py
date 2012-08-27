from ftw.notification.base.browser.views import NotificationForm as base
from ftw.table.interfaces import ITableGenerator
from zope.component import queryUtility

def checkbox_selected_helper(item, value):
    if item['selected'] == True:
        return u"""<input type="checkbox"
                          name="to_list:list"
                          checked="checked"
                          value="%s"/>""" % item['value']


    return u"""<input type="checkbox"
                      name="to_list:list"
                      value="%s"/>""" % item['value']




class NotificationForm(base):
    """Notification with preselect for tickets"""

    @property
    def columns(self):
        columns = super(NotificationForm, self).columns
        columns[0]['transform'] = checkbox_selected_helper
        return columns

    def __init__(self, context, request):
        super(NotificationForm, self).__init__(context, request)
        self.pre_select = []

        self.pre_select.append(self.context.getResponsibleManager())


    def render_listing(self):
        generator = queryUtility(ITableGenerator, 'ftw.tablegenerator')
        final_users = []
        for user in self.users:
            user['selected'] = False
            if user['value'] in self.pre_select:
                user['selected'] = True
            final_users.append(user)

        return generator.generate(final_users, self.columns, sortable=('name'))
