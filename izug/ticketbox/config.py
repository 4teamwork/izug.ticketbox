"""Common configuration constants
"""

PROJECTNAME = 'izug.ticketbox'

ADD_PERMISSIONS = {
    # -*- extra stuff goes here -*-
    'Ticket': 'izug.ticketbox: Add Ticket',
    'TicketBox': 'izug.ticketbox: Add Ticket Box',
}
INDEXES = (('getState', 'FieldIndex'),
            ('getReleases', 'FieldIndex'),
            ('getWatchedRelease', 'FieldIndex'),
            ('getArea', 'FieldIndex'),
            ('getVariety', 'FieldIndex'),
            ('getPriority', 'FieldIndex'),
            ('getResponsibleManager', 'FieldIndex'),
            ('getDueDate', 'DateIndex'),
            ('sortable_id', 'FieldIndex'),
            ('sortable_responsibleManager', 'FieldIndex'),
            ('sortable_ticket_references', 'FieldIndex'),
            ('get_owner_index', 'FieldIndex'),
           ('ticketbox_title', 'FieldIndex'),
           )

# Add text/html to the list of mimetypes to allow HTML/kupu
# issue/response text.
ISSUE_MIME_TYPES = ('text/html', )
DEFAULT_ISSUE_MIME_TYPE = 'text/html'
