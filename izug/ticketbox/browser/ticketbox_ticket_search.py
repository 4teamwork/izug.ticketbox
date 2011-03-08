from izug.arbeitsraum.browser.views import MyListing, icon, izug_files_linked, delete_action


class TicketBoxSearch(MyListing):

    types = 'Ticket'

    sort_on = 'id'

    columns = (
               ('Typ', 'getContentType', icon),
               ('Title', 'Title', izug_files_linked),
               ('', delete_action),
               )

