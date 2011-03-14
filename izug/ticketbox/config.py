"""Common configuration constants
"""

PROJECTNAME = 'izug.ticketbox'

ADD_PERMISSIONS = {
    # -*- extra stuff goes here -*-
    'Ticket': 'izug.ticketbox: Add Ticket',
    'TicketBox': 'izug.ticketbox: Add Ticket Box',
}
INDEXES = (('State', 'FieldIndex'),
            ('Releases', 'FieldIndex'),
            ('Area', 'FieldIndex'),
            ('Priority', 'FieldIndex'),
            ('responsibleManager', 'FieldIndex'),
            ('Due_date', 'FieldIndex'),
            ('sortable_id', 'FieldIndex'),
           )


# Add text/html to the list of mimetypes to allow HTML/kupu
# issue/response text.
ISSUE_MIME_TYPES = ('text/x-web-intelligent', )
DEFAULT_ISSUE_MIME_TYPE = 'text/x-web-intelligent'