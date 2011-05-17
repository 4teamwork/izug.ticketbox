from Products.contentmigration.walker import CustomQueryWalker
from izug.ticketbox.handlers import generate_datagrid_column_id, move_document_to_reference
from Products.contentmigration.basemigrator.migrator import CMFFolderMigrator, CMFItemMigrator
from DateTime import DateTime

class PoiTrackerToTicketbox(CMFFolderMigrator):
    """Migrate poi tracker to ticketbox"""

    walker = CustomQueryWalker
    src_meta_type = "PoiTracker"
    src_portal_type = "PoiTracker"
    dst_meta_type = "Ticket Box"
    dst_portal_type = "Ticket Box"
    safeMigration = False

    def migrate_states(self):
        """Migrate poi workflow states to ticketbox states"""
        states = self.old.getIssueWorkflowStates()

        new_states = []
        for state in states.items():

            new_states.append(
                {
                'id':state[0],
                'title':state[1],
                'show_in_all_tickets': '1',
                'show_in_my_tickets': '1',
                })

        self.new.setAvailableStates(new_states)

    def migrate_areas(self):
        """Migrate poi areas to ticketbox areas"""

        self.new.setAvailableAreas(self.old.availableAreas)

    def migrate_priorities(self):
        """Migrate poi severities to ticketbox priorities"""

        priorities = self.old.availableSeverities

        new_priorities = []
        for prioritie in priorities:

            new_priorities.append(
                {
                'title':prioritie,
                })

        self.new.setAvailablePriorities(new_priorities)

    def migrate_releases(self):
        """Migrate poi releases to ticketbox releases"""

        releases = self.old.availableReleases

        new_releases = []
        for release in releases:

            new_releases.append(
                {
                'title':release,
                })

        self.new.setAvailableReleases(new_releases)

    def migrate_z_create_ids(self):
        generate_datagrid_column_id(self.new,'new')


class PoiIssueToTicketboxTicket(CMFItemMigrator):
    """Migrate the old item type to the new item type
    """

    walker = CustomQueryWalker
    src_meta_type = "PoiIssue"
    src_portal_type = "PoiIssue"
    dst_meta_type = "Ticket"
    dst_portal_type = "Ticket"
    safeMigration = False
    map = {'issue_title':'title',
           'responsibleManager':'responsibleManager',
           'endDate':'dueDate',
           'Creator':'setCreators',
           }

    def migrate_map_state(self):

        wftool = self.old.portal_workflow
        self.new.setState(wftool.getInfoFor(self.old, 'review_state'))

    def migrate_map_area(self):
        self.map_area(self.old.getArea())

    def map_area(self, old_area):

        areas = self.new.aq_parent.getAvailableAreas()

        for area in areas:
            if old_area == area['title']:
                self.new.setArea(area['id'])
                continue

    def migrate_map_priority(self):

        self.map_priority(self.old.getSeverity())

    def map_priority(self, old_priority):

        priorities = self.new.aq_parent.getAvailablePriorities()


        for priority in priorities:
            if old_priority == priority['title']:
                self.new.setPriority(priority['id'])
                continue

    def migrate_map_release(self):
        """Migrate the poi releases to ticket releases"""

        self.map_release(self.old.getRelease())

    def map_release(self, old_release):

        releases = self.new.aq_parent.getAvailableReleases()

        for release in releases:
            if old_release == release['title']:
                self.new.setReleases(release['id'])
                continue

    def migrate_map_description(self):
        """Migrate the poi Details and Steps to ticket description"""

        desc = self.old.getDetails() + "<br /> <br />" + self.old.getSteps()
        self.new.setDescription(desc)

    def migrate_attachments(self):
        """Migrate the poi attachments to ticket attachments"""
        # move_document_to_reference(self.new, 'move')

    def migrate_response(self):
        """Migrate all poi responses from this ticket to ticketbox responses"""

        # Get old responses
        responses = self.old.folderlistingFolderContents()

        # In the old responses there are just translatet workflowstates or
        # transistion ids. But we need the state-id. So we have to find the
        # transition and get the destination state id.
        wftool = self.old.portal_workflow.poi_issue_workflow.transitions

        # The ticketbox make a default AnswerDate and if we create a new answer,
        # the the first response change the answerdate.
        # So we have to set the answerdate from the ticket to a empty string.
        self.new.setAnswerDate('')

        for response in responses:

            text = response.response()
            responsibleManager = response.newResponsibleManager

            # Here we get the transition id from the old response and search in
            # the workflow-tool for the destination-state-id of this transition
            transition_id = response.getIssueTransition()
            state = ''
            if transition_id:
                state = wftool.get(transition_id).new_state_id
            priority = self.map_priority(response.newSeverity)
            release = self.map_release(response.newTargetRelease)
            # attachment = response.getAttachment()
            # if attachment:
            #     import pdb; pdb.set_trace( )

            setattr(self.new.REQUEST, 'form',
                {'response':text,
                'responsibleManager':responsibleManager,
                'state':state,
                'priority':priority,
                'releases':release,
                # 'attachment':attachment
                })

            # We call the create_response-view. This view is getting the form and
            # reads the params of this form and create the response
            self.new.restrictedTraverse('@@create_response')()

            # Because the response of the ticketbox set the creater and the creationdate
            # with the logged in user and the actual date, we need to set this attributes
            # manually after creation the response
            new_response = self.new.restrictedTraverse('@@base_response').responses()
            new_response = new_response[len(new_response)-1].get('response')
            new_response.creator = response.Creator()
            new_response.date = DateTime(response.Date())
