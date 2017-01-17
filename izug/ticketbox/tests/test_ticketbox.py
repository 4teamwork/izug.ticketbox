from copy import deepcopy
from ftw.builder import Builder
from ftw.builder import create
from izug.ticketbox.browser.helper import map_attribute
from izug.ticketbox.testing import TICKETBOX_INTEGRATION_TESTING
from izug.ticketbox.tests import helpers
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.Archetypes.event import ObjectEditedEvent
from Products.CMFCore.utils import getToolByName
from unittest2 import TestCase
from zope.component import getMultiAdapter
from zope.event import notify


def get_ids_and_titles(data):
    """Returns all ids and titles of the dicts within the list data.
    """
    return [(item.get('id'), item.get('title')) for item in data]


class TestTicketBox(TestCase):

    layer = TICKETBOX_INTEGRATION_TESTING

    def setUp(self):
        super(TestTicketBox, self).setUp()
        self.portal = self.layer['portal']
        self.wf_tool = getToolByName(self.portal, 'portal_workflow')
        self.wf_tool.setDefaultChain('simple_publication_workflow')
        helpers.login_as_manager(self.portal)

        self.catalog = getToolByName(self.portal, 'portal_catalog')

        self.ticketbox = helpers.create_ticketbox(self.portal)
        self.ticket1 = helpers.create_ticket(self.ticketbox)
        self.ticket2 = helpers.create_ticket(self.ticketbox, data_index=1)

    def tearDown(self):
        helpers.logout_manager(self.portal)
        super(TestTicketBox, self).tearDown()

    def test_required_fields(self):
        title = self.ticketbox.getField('title')
        description = self.ticketbox.getField('description')

        self.assertEquals(title.required, True)
        self.assertEquals(description.required, False)

    def test_generated_id(self):
        state = self.ticketbox.getAvailableStates()[2]['id']
        area = self.ticketbox.getAvailableAreas()[2]['id']
        release = self.ticketbox.getAvailableReleases()[2]['id']
        priority = self.ticketbox.getAvailablePriorities()[2]['id']

        self.assertEquals(state, "test-id-state")
        self.assertEquals(area, "test-id-area")
        self.assertEquals(release, "test-id-release")
        self.assertEquals(priority, "test-id-priority")

    def test_overview_view(self):

        def get_filtered_tickets(filterid, filtervalue):
            self.portal.REQUEST.set('filterid', filterid)
            self.portal.REQUEST.set('filtervalue', filtervalue)
            view = getMultiAdapter(
                (self.ticketbox, self.portal.REQUEST),
                name='tabbedview_view-overview')
            view.update()
            contents = view.contents
            self.portal.REQUEST.set('filterid', None)
            self.portal.REQUEST.set('filtervalue', None)
            return contents

        ticket_state = get_filtered_tickets('getState', 'show-all-tickets')
        ticket_area = get_filtered_tickets('getArea', 'internet')
        ticket_priority = get_filtered_tickets('getPriority', 'high')
        ticket_responsible = get_filtered_tickets('getResponsibleManager',
                                                  'test_user_1_')

        self.assertEquals(ticket_state[0].getObject().getState(), "show-all-tickets")
        self.assertEquals(ticket_area[0].getObject().getArea(), "internet")
        self.assertEquals(ticket_priority[0].getObject().getPriority(),
                          "high")
        self.assertEquals(
            ticket_responsible[0].getObject().getResponsibleManager(),
            "test_user_1_")

    def test_all_tickets_view(self):
        ticketbox_view = getMultiAdapter(
            (self.ticketbox, self.portal.REQUEST),
            name='tabbedview_view-all_tickets')
        ticketbox_view.update()

        self.assertEquals(len(ticketbox_view.contents), 1)

    def test_my_tickets_view(self):
        ticketbox_view = getMultiAdapter(
            (self.ticketbox, self.portal.REQUEST),
            name='tabbedview_view-my_tickets')
        ticketbox_view.update()

        self.assertEquals(len(ticketbox_view.contents), 1)

    def test_unassigned_is_assignable(self):
        self.assertIn(
            ('(UNASSIGNED)', u'None'),
            self.ticketbox.assignable_users())

    def test_make_user_not_assignable(self):
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        field = self.ticketbox.getField('assignable_user_ids')
        mutator = field.getMutator(self.ticketbox)

        self.ticketbox.manage_setLocalRoles(
            'test_user_1_', ['Contributor', 'Reader'])
        self.assertIn(
            ('test_user_1_', 'test-user'),
            self.ticketbox.assignable_users())

        mutator([])
        self.assertNotIn(
            ('test_user_1_', 'test-user'),
            self.ticketbox.assignable_users())

        mutator(['test_user_1_'])
        self.assertIn(
            ('test_user_1_', 'test-user'),
            self.ticketbox.assignable_users())

    def test_new_user_gets_assignable_automatically(self):
        user1 = create(Builder('user'))
        #You should never set localroles on a plonesite but we do it here since
        # it is our only parent and we do require local roles.
        self.portal.manage_setLocalRoles(
            'john.doe', ['Contributor', 'Reader'])
        self.assertIn(
            ('john.doe', 'Doe John'),
            self.ticketbox.assignable_users())

    def test_only_with_add_permission(self):
        user1 = create(Builder('user'))
        user2 = create(Builder('user').named('James','Bond'))
        self.ticketbox.manage_setLocalRoles(
            user1.id, ['Contributor', 'Reader'])
        self.ticketbox.manage_setLocalRoles(
            user2.id, ['Reader'])

        self.assertIn(
            ('john.doe', 'Doe John'),
            self.ticketbox.assignable_users())

        self.assertNotIn(
            ('james.bond', 'Bond James'),
            self.ticketbox.assignable_users())

    def test_duplicate_state_ids(self):
        # When changing a state and adding a state in a specific way it
        # should not result in duplicate state ids.

        states = [{'id': '',
                   'title': 'Open',
                   'show_in_all_tickets': '1',
                   'show_in_my_tickets': '1'}]
        self.ticketbox.setAvailableStates(states)
        notify(ObjectEditedEvent(self.ticketbox))

        states = self.ticketbox.getAvailableStates()
        self.assertEqual(len(states), 1)
        self.assertEqual(get_ids_and_titles(states), [('open', 'Open')])

        states = list(deepcopy(states))
        states.append({'id': '',
                       'title': 'Open',
                       'show_in_all_tickets': '1',
                       'show_in_my_tickets': '1'})
        self.ticketbox.setAvailableStates(states)
        notify(ObjectEditedEvent(self.ticketbox))

        states = self.ticketbox.getAvailableStates()
        self.assertEqual(len(states), 2)
        self.assertEqual(get_ids_and_titles(states), [
                ('open', 'Open'),
                ('open-1', 'Open')])

    def test_duplicate_release_ids(self):
        releases = [{'id': '',
                     'title': '1.x'}]
        self.ticketbox.setAvailableReleases(releases)
        notify(ObjectEditedEvent(self.ticketbox))

        releases = self.ticketbox.getAvailableReleases()
        self.assertEqual(len(releases), 1)
        self.assertEqual(get_ids_and_titles(releases), [('1-x', '1.x')])

        releases = list(deepcopy(releases))
        releases.append({'id': '',
                         'title': '1.x'})
        self.ticketbox.setAvailableReleases(releases)
        notify(ObjectEditedEvent(self.ticketbox))

        releases = self.ticketbox.getAvailableReleases()
        self.assertEqual(len(releases), 2)
        self.assertEqual(get_ids_and_titles(releases),
                         [('1-x', '1.x'),
                          ('1-x-1', '1.x')])

    def test_sorted_tickets_after_changing_datagrid_titles(self):
        STATE_DATA = [
            {'id': '',
             'title': "A state",
             'show_in_all_tickets': '1',
             'show_in_my_tickets': '0',
             },

            {'id': '',
             'title': "B state",
             'show_in_all_tickets': '0',
             'show_in_my_tickets': '1',
             },

            {'id': '',
             'title': "C state",
             'show_in_all_tickets': '1',
             'show_in_my_tickets': '1',
             }]

        # Set new states to the ticketbox and let it generate the
        # ids for each state by notify the edited-event.
        self.ticketbox.setAvailableStates(STATE_DATA)
        notify(ObjectEditedEvent(self.ticketbox))

        states = self.ticketbox.getAvailableStates()

        # Use the new states for the tickets
        self.ticket1.setState(states[2].get('id'))
        self.ticket1.setTitle('Ticket 1')
        self.ticket1.reindexObject()

        self.ticket2.setState(states[0].get('id'))
        self.ticket2.setTitle('Ticket 2')
        self.ticket2.reindexObject()

        query = {'portal_type': 'Ticket', 'sort_on': 'getState'}

        # Check the sorting by state
        tickets = [ticket.getObject() for ticket in self.catalog(query)]
        self.assertEqual(
            [['A state', 'Ticket 2'], ['C state', 'Ticket 1']],
            [[map_attribute(ticket, "state"), ticket.Title()] for ticket in tickets])

        # Rename the title of the first state in the ticketbox...
        states[0]['title'] = 'D state'
        notify(ObjectEditedEvent(self.ticketbox))

        # And check the sort-order of the tickets again
        tickets = [ticket.getObject() for ticket in self.catalog(query)]
        self.assertEqual(
            [['C state', 'Ticket 1'], ['D state', 'Ticket 2']],
            [[map_attribute(ticket, "state"), ticket.Title()] for ticket in tickets],
            "The sort-order should have been changed because we changed the state title "
            "on the ticketbox.")
