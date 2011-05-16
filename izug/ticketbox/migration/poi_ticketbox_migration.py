from Products.contentmigration.walker import CustomQueryWalker
from Products.contentmigration.archetypes import ATItemMigrator

BASE_AT_PROPERTIES = dict(title='title',
                               description='description',
                               text='text',
                               subject='subject',
                               relatedItems='relatedItems',
                               location='location',
                               language='language',
                               effectiveDate='effectiveDate',
                               expirationDate='expirationDate',
                               creation_date='creation_date',
                               modification_date='modification_date',
                               creators='creators',
                               contributors='contributors',
                               rights='rights',
                               allowDiscussion='allowDiscussion',
                               excludeFromNav='excludeFrom')

def get_map():
    map_ = BASE_AT_PROPERTIES
    map_['responsibleManager'] = 'responsibleManager'
    map_['area'] = 'area'
    map_['severity'] = 'priority'
    map_['targetRelease'] = 'releases'
    map_['endDate'] = 'dueDate'
    map_['issueTransition'] = 'state'
    map_['issue_title'] = 'title'
    return map_

class PoiIssueToTicketboxTicket(object, ATItemMigrator):
    """Migrate the old item type to the new item type
    """

    walker = CustomQueryWalker
    src_meta_type = "PoiIssue"
    src_portal_type = "PoiIssue"
    dst_meta_type = "Ticket"
    dst_portal_type = "Ticket"
    description = "PoiIssue to Ticketbox Ticket"
    safeMigration = False

    def __init__(self, *args, **kwargs):
        ATItemMigrator.__init__(self, *args, **kwargs)
        self.fields_map = get_map()

    def migrate_desc_state(self):
        """"""

    def migrate_response(self):

        responses =

        for response in responses

            responsibiltyManager =
            state =
            area =

            self.new.REQUEST.set('form', {})
            self.new.restritedTravers('@@create_reponse')()




PoiIssueToTicketboxTicketMigrator = PoiIssueToTicketboxTicket


