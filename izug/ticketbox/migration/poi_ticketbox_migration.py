from DateTime import DateTime
from izug.ticketbox.handlers import \
    generate_datagrid_column_id, \
    move_document_to_reference
from Products.contentmigration.walker import CustomQueryWalker
from Products.contentmigration.basemigrator.migrator import \
    CMFFolderMigrator, \
    CMFItemMigrator


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
                'id': state[0],
                'title': state[1],
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
                'title': prioritie,
                })

        self.new.setAvailablePriorities(new_priorities)

    def migrate_releases(self):
        """Migrate poi releases to ticketbox releases"""

        releases = self.old.availableReleases

        new_releases = []
        for release in releases:

            new_releases.append(
                {
                'title': release,
                })

        self.new.setAvailableReleases(new_releases)

    def last_migrate_create_ids(self):
        generate_datagrid_column_id(self.new, 'new')


class PoiIssueToTicketboxTicket(CMFItemMigrator):
    """Migrate the old item type to the new item type
    """

    walker = CustomQueryWalker
    src_meta_type = "PoiIssue"
    src_portal_type = "PoiIssue"
    dst_meta_type = "Ticket"
    dst_portal_type = "Ticket"
    safeMigration = False
    user_mapping = {}
    map = {'issue_title': 'title',
           'endDate': 'dueDate',
           'getAttachment':'setAttachment'
           }

    def migrate_map_state(self):

        wftool = self.old.portal_workflow
        self.new.setState(wftool.getInfoFor(self.old, 'review_state'))

    def migrate_map_area(self):
        self.map_area(self.old.getArea())

    def migrate_map_priority(self):

        self.map_priority(self.old.getSeverity())

    def migrate_map_release(self):
        """Migrate the poi releases to ticket releases"""

        self.map_release(self.old.getRelease())

    def migrate_map_description(self):
        """Migrate the poi Details and Steps to ticket description"""

        desc = self.old.getDetails() + "<br /> <br />" + self.old.getSteps()
        self.new.setDescription(desc)

    def migrate_map_responsible(self):
        """Migrate the poi responsibleManager to
        ticketbox responbsible Manager"""

        self.new.setResponsibleManager(
            self.map_username(self.old.getResponsibleManager()))

    def migrate_response(self):
        """Migrate all poi responses from this ticket to ticketbox responses"""

        # Get old responses
        responses = self.old.folderlistingFolderContents()

        # In the old responses there are just translatet workflowstates or
        # transistion ids. But we need the state-id. So we have to find the
        # transition and get the destination state id.
        wftool = self.old.portal_workflow.stv_issue_workflow.transitions

        # The ticketbox make a default AnswerDate and if we create a new
        # answer, the the first response change the answerdate.
        # So we have to set the answerdate from the ticket to a empty string.
        self.new.setAnswerDate('')

        for i, response in enumerate(responses):

            text = response.response()
            responsibleManager = self.map_username(
                response.newResponsibleManager)
            # Here we get the transition id from the old response and search in
            # the workflow-tool for the destination-state-id of this transition
            transition = wftool.get(response.getIssueTransition())
            state = ''
            if transition:
                    state = transition.new_state_id
            priority = self.map_priority(response.newSeverity)
            release = self.map_release(response.newTargetRelease)

            file_ = response.getAttachment()

            # Its possible that we become 2 ore more files with the same filename.
            # We have to change the attachments filename that we don't get a
            # file-already-exist error.
            if file_.data != '':

                attachment = file_.data

                try:
                    filename_ = attachment.filename.split('.')
                    if len(filename_) > 1:
                        name = '.'.join(filename_[:len(filename_)-1]) + '_%s' % i
                        name = name + '.%s' % filename_[len(filename_)-1]
                    else:
                        filename_.append(str(i))
                        name = '.'.join(filename_)

                    attachment.filename = name
                except:
                    print "*****File from ticket %s failed" % self.new.absolute_url()
                    attachment = ''

            else:
                attachment = ''

            setattr(self.new.REQUEST, 'form',
                {'response': text,
                'responsibleManager': responsibleManager,
                'state': state,
                'priority': priority,
                'releases': release,
                'attachment': attachment,
                })

            # We call the create_response-view. This view is getting the form
            # and reads the params of this form and create the response
            self.new.restrictedTraverse('@@create_response')(redirect=False)

            # Because the response of the ticketbox set the creater and the
            # creationdate with the logged in user and the actual date,
            # we need to set this attributes manually after
            # creation the response

            try:
                new_response = self.new.restrictedTraverse(
                    '@@base_response').responses()

                new_response = new_response[len(new_response)-1].get('response')

                new_response.creator = self.map_username(response.Creator())
                new_response.date = DateTime(response.Date())
            except:
                print "--------Response at %s failed" % self.new.absolute_url()

    def last_migrate_creator(self):
        """set the creator of the ticket"""

        self.new.setCreators(self.map_username(self.old.Creator()))

    def last_migrate_attachments(self):
        """Migrate the poi attachments to ticket attachments"""
        # move_document_to_reference(self.new, 'move')

    def map_area(self, old_area):

        areas = self.new.aq_parent.getAvailableAreas()

        for area in areas:
            if old_area == area['title']:
                self.new.setArea(area['id'])
                continue

    def map_username(self, uid):
        """maps old userids with new userids"""

        # We need to map old user ids (user.name) with new ids (USNA)
        # If there is nothing to map, we return the old id
        responsibleManager = self.user_mapping.get(uid)
        if responsibleManager:
            return responsibleManager
        else:
            return uid

    def map_release(self, old_release):

        releases = self.new.aq_parent.getAvailableReleases()

        for release in releases:
            if old_release == release['title']:
                self.new.setReleases(release['id'])
                continue

    def map_priority(self, old_priority):

        priorities = self.new.aq_parent.getAvailablePriorities()

        for priority in priorities:
            if old_priority == priority['title']:
                self.new.setPriority(priority['id'])
                continue