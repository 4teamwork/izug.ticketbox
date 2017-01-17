from copy import deepcopy
from ftw.builder import Builder
from ftw.builder import create
from izug.ticketbox.interfaces import ITicketboxDatagridIdUpdater
from izug.ticketbox.testing import TICKETBOX_FUNCTIONAL_TESTING
from izug.ticketbox.tests import helpers
from izug.ticketbox.tests.data import STATE_DATA
from Products.Archetypes.event import ObjectEditedEvent
from unittest2 import TestCase
from zope.event import notify


class TestTicketboxDatagridIdUpdater(TestCase):

    layer = TICKETBOX_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestTicketboxDatagridIdUpdater, self).setUp()
        portal = self.layer['portal']
        helpers.login_as_manager(portal)

    def test_generate_ids_on_creation(self):
        states = [
            {'id': '',
             'title': "Chuck Norris",
             'show_in_all_tickets': '1',
             'show_in_my_tickets': '0',
             }]

        ticketbox = create(Builder('ticket box')
                           .titled('The Ticket Box')
                           .having(
                               availableStates=states))

        self.assertEqual(
            'chuck-norris',
            ticketbox.getAvailableStates()[0].get('id'))

    def test_regenerate_datagrid_ids_if_title_was_modified(self):
        states = [
            {'id': 'chuck-norris',
             'title': "Chuck Norris",
             'show_in_all_tickets': '1',
             'show_in_my_tickets': '0',
             }]

        ticketbox = create(Builder('ticket box')
                           .titled('The Ticket Box')
                           .having(
                               availableStates=states))

        ticketbox.getAvailableStates()[0]['title'] = "James Bond"
        notify(ObjectEditedEvent(ticketbox))

        self.assertEqual(
            'james-bond',
            ticketbox.getAvailableStates()[0].get('id'))

    def test_update_tickets_if_title_of_ticketbox_datagrid_was_modified(self):
        states = [
            {'id': 'chuck-norris',
             'title': "Chuck Norris",
             'show_in_all_tickets': '1',
             'show_in_my_tickets': '0',
             }]

        ticketbox = create(Builder('ticket box')
                           .titled('The Ticket Box')
                           .having(
                               availableStates=states))

        ticket = create(Builder('ticket')
                        .within(ticketbox)
                        .having(state='chuck-norris'))

        ticketbox.getAvailableStates()[0]['title'] = "James Bond"
        notify(ObjectEditedEvent(ticketbox))

        self.assertEqual('james-bond', ticket.getState())

    def test_do_not_update_tickets_from_other_ticketboxes(self):
        states = [
            {'id': 'chuck-norris',
             'title': "Chuck Norris",
             'show_in_all_tickets': '1',
             'show_in_my_tickets': '0',
             }]

        ticketbox_1 = create(Builder('ticket box')
                             .titled('The Ticket Box 1')
                             .having(
                                 availableStates=list(deepcopy(states))))

        ticketbox_2 = create(Builder('ticket box')
                             .titled('The Ticket Box 2')
                             .having(
                                 availableStates=list(deepcopy(states))))

        ticket_1 = create(Builder('ticket')
                          .within(ticketbox_1)
                          .having(state='chuck-norris'))

        ticket_2 = create(Builder('ticket')
                          .within(ticketbox_2)
                          .having(state='chuck-norris'))

        ticketbox_1.getAvailableStates()[0]['title'] = "James Bond"
        notify(ObjectEditedEvent(ticketbox_1))
        notify(ObjectEditedEvent(ticketbox_2))

        self.assertEqual('james-bond', ticket_1.getState())
        self.assertEqual('chuck-norris', ticket_2.getState())


class TestUpdate(TestCase):

    layer = TICKETBOX_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestUpdate, self).setUp()
        portal = self.layer['portal']
        helpers.login_as_manager(portal)

        self.ticketbox = create(Builder('ticket box')
                                .titled('The Ticket Box')
                                .having(
                                    availableStates=list(deepcopy(STATE_DATA))))

        self.adapter = ITicketboxDatagridIdUpdater(self.ticketbox)

    def test_do_not_update_if_nothing_changed(self):
        ticket = create(Builder('ticket')
                        .within(self.ticketbox)
                        .having(state='show-all-tickets'))

        self.assertEqual(0, len(self.adapter.update()))
        self.assertEqual('show-all-tickets', ticket.getState())

    def test_update_all_tickets_if_something_changed_on_datagrid(self):
        ticket_1 = create(Builder('ticket')
                          .within(self.ticketbox)
                          .having(state='show-all-tickets'))

        ticket_2 = create(Builder('ticket')
                          .within(self.ticketbox)
                          .having(state='show-my-tickets'))

        self.ticketbox.getAvailableStates()[0]['title'] = "Chuck Norris"

        self.assertEqual(1, len(self.adapter.update()))
        self.assertEqual('chuck-norris', ticket_1.getState())
        self.assertEqual(
            'chuck-norris',
            self.ticketbox.getAvailableStates()[0].get('id'))


class TestUpdateTickets(TestCase):

    layer = TICKETBOX_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestUpdateTickets, self).setUp()
        portal = self.layer['portal']
        helpers.login_as_manager(portal)

        self.ticketbox = create(Builder('ticket box')
                                .titled('THe Ticket Box'))

        self.adapter = ITicketboxDatagridIdUpdater(self.ticketbox)

    def test_do_not_update_tickets_if_nothing_changed(self):
        self.adapter.changes = {}

        self.assertEqual([], self.adapter.update_tickets())

    def test_do_not_update_ticket_if_no_related_attribute_changed(self):
        ticket = create(Builder('ticket')
                        .within(self.ticketbox)
                        .having(state='foo'))

        self.adapter.changes = {'availableAreas': [('foo', 'bar')]}

        self.assertEqual(0, len(self.adapter.update_tickets()))
        self.assertEqual('foo', ticket.getState())

    def test_do_not_update_ticket_if_the_id_was_never_generated_before(self):
        ticket = create(Builder('ticket')
                        .within(self.ticketbox)
                        .having(state='foo'))

        self.adapter.changes = {'availableStates': [('', 'bar')]}

        self.assertEqual(0, len(self.adapter.update_tickets()))
        self.assertEqual('foo', ticket.getState())

    def test_do_not_update_ticket_if_the_changed_id_is_not_related_to_the_ticket(self):
        ticket = create(Builder('ticket')
                        .within(self.ticketbox)
                        .having(state='foo'))

        self.adapter.changes = {'availableStates': [('bar', 'chuck')]}

        self.assertEqual(0, len(self.adapter.update_tickets()))
        self.assertEqual('foo', ticket.getState())

    def test_update_ticket_if_related_id_changed(self):
        ticket = create(Builder('ticket')
                        .within(self.ticketbox)
                        .having(state='foo'))

        self.assertEqual(1, len(self.adapter.update_tickets(
            {'availableStates': [('foo', 'bar')]})))
        self.assertEqual('bar', ticket.getState())

    def test_update_multiple_tickets_works_properly(self):
        ticket_1 = create(Builder('ticket')
                          .within(self.ticketbox)
                          .having(state='foo'))

        ticket_2 = create(Builder('ticket')
                          .within(self.ticketbox)
                          .having(state='foo'))

        ticket_3 = create(Builder('ticket')
                          .within(self.ticketbox)
                          .having(state='chuck'))

        self.assertEqual(2, len(self.adapter.update_tickets(
            {'availableStates': [('foo', 'bar')]})))
        self.assertEqual('bar', ticket_1.getState())
        self.assertEqual('bar', ticket_2.getState())
        self.assertEqual('chuck', ticket_3.getState())


class TestUniquifyIds(TestCase):

    layer = TICKETBOX_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestUniquifyIds, self).setUp()
        portal = self.layer['portal']
        helpers.login_as_manager(portal)

        ticketbox = create(Builder('ticket box')
                           .titled('THe Ticket Box'))

        self.adapter = ITicketboxDatagridIdUpdater(ticketbox)

    def test_new_ids_set(self):
        input = [{'id': '', 'title': 'Foo'},
                 {'id': '', 'title': 'Bar'}]

        updated = [{'id': 'foo', 'title': 'Foo'},
                   {'id': 'bar', 'title': 'Bar'}]

        self.adapter.uniquify_ids(input)

        self.assertEqual(updated, input)

    def test_partical_ids(self):
        input = [{'id': 'foo', 'title': 'Foo'},
                 {'id': '', 'title': 'Bar'}]

        updated = [{'id': 'foo', 'title': 'Foo'},
                   {'id': 'bar', 'title': 'Bar'}]

        self.adapter.uniquify_ids(input)

        self.assertEqual(updated, input)

    def test_conflicting_ids(self):
        input = [{'id': '', 'title': 'Foo'},
                 {'id': '', 'title': 'Foo'},
                 {'id': '', 'title': 'Foo'}]

        updated = [{'id': 'foo', 'title': 'Foo'},
                   {'id': 'foo-1', 'title': 'Foo'},
                   {'id': 'foo-2', 'title': 'Foo'}]

        self.adapter.uniquify_ids(input)

        self.assertEqual(updated, input)

    def test_modification_updateds_ids(self):
        input = [{'id': 'foo', 'title': 'Bar'}]

        updated = [{'id': 'bar', 'title': 'Bar'}]

        self.adapter.uniquify_ids(input)

        self.assertEqual(updated, input)

    def test_keeps_other_keys(self):
        input = [{'id': 'foo', 'title': 'Foo', 'bar': 'Bar'}]
        updated = [{'id': 'foo', 'title': 'Foo', 'bar': 'Bar'}]

        self.adapter.uniquify_ids(input)

        self.assertEqual(updated, input)

    def test_prevent_conflicting_if_rename_to_existing(self):
        input = [{'id': 'foo', 'title': 'Bar'},
                 {'id': 'bar', 'title': 'Foo'}]

        updated = [{'id': 'bar-1', 'title': 'Bar'},
                   {'id': 'foo-1', 'title': 'Foo'}]

        self.adapter.uniquify_ids(input)

        self.assertEqual(updated, input)

    def test_does_not_copy(self):
        input = [{'id': '', 'title': 'Foo'}]

        id_input = id(input)

        self.adapter.uniquify_ids(input)

        self.assertEqual(id_input, id(input))

    def test_return_value_is_empty_if_nothing_has_changed(self):
        input = [{'id': 'foo', 'title': 'Foo'}]

        changes = self.adapter.uniquify_ids(input)

        self.assertEqual([], changes)

    def test_return_value_contains_all_changes(self):
        input = [{'id': 'foo', 'title': 'Foo'},
                 {'id': 'bar-1', 'title': 'Bar'},
                 {'id': '', 'title': 'Chuck'}]

        changes = self.adapter.uniquify_ids(input)

        self.assertEqual([('bar-1', 'bar'), ('', 'chuck')], changes)


class TestCreateUniqueId(TestCase):

    layer = TICKETBOX_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestCreateUniqueId, self).setUp()
        portal = self.layer['portal']
        helpers.login_as_manager(portal)

        ticketbox = create(Builder('ticket box')
                           .titled('THe Ticket Box'))

        self.adapter = ITicketboxDatagridIdUpdater(ticketbox)

    def test_first_id(self):
        self.assertEqual(self.adapter.create_uniqe_id('Foo', []), 'foo')

    def test_existing_id(self):
        self.assertEqual(
            self.adapter.create_uniqe_id('Foo', ['foo']), 'foo-1')

        self.assertEqual(
            self.adapter.create_uniqe_id('Foo', ['foo', 'foo-1']), 'foo-2')

    def test_spaces(self):
        self.assertEqual(
            self.adapter.create_uniqe_id('Foo bar', []), 'foo-bar')
