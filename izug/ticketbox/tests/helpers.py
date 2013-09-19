from Acquisition import aq_inner, aq_parent
from izug.ticketbox.adapters import ResponseContainer
from izug.ticketbox.handlers import generate_datagrid_column_id
from izug.ticketbox.tests.data import AREA_DATA
from izug.ticketbox.tests.data import PRIORITY_DATA
from izug.ticketbox.tests.data import RELEASE_DATA
from izug.ticketbox.tests.data import STATE_DATA
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles


def login_as_manager(portal):
    setRoles(portal, TEST_USER_ID, ['Manager'])
    login(portal, TEST_USER_NAME)


def logout_manager(portal):
    setRoles(portal, TEST_USER_ID, ['Member'])
    logout()


def create_ticketbox(container, id_='ticketbox'):
    ticketbox = container.get(container.invokeFactory('Ticket Box', id_))

    ticketbox.getField('title').set(ticketbox, "Ticket Box Title")
    ticketbox.getField('description').set(
        ticketbox, "A TicketBox description")

    ticketbox.setIndividualIdentifier("ABC123")
    ticketbox.setAvailableStates(STATE_DATA)
    ticketbox.setAvailableReleases(RELEASE_DATA)
    ticketbox.setAvailableAreas(AREA_DATA)
    ticketbox.setAvailablePriorities(PRIORITY_DATA)

    generate_datagrid_column_id(ticketbox, None)
    ticketbox.reindexObject()

    return ticketbox


def remove_obj(obj):
    parent = aq_parent(aq_inner(obj))
    parent.manage_delObjects([obj.id])


def create_ticket(ticketbox, id_=None, data_index=0):
    id_ = id_ or 'ticket%i' % data_index
    ticket = ticketbox.get(ticketbox.invokeFactory('Ticket', id_))

    ticket.getField('title').set(ticket, "Ticket Title")
    ticket.getField('description').set(ticket, "A Ticket description")
    ticket.getField('state').set(ticket, STATE_DATA[data_index]['id'])
    ticket.getField('area').set(ticket, AREA_DATA[data_index]['id'])
    ticket.getField('priority').set(ticket, PRIORITY_DATA[data_index]['id'])
    ticket.getField('releases').set(ticket, RELEASE_DATA[data_index]['id'])
    ticket.getField('responsibleManager').set(ticket, "test_user_1_")

    ticket.reindexObject()
    ResponseContainer(ticket)

    return ticket
