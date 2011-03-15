from izug.ticketbox import ticketboxMessageFactory as _

def map_attribute(context, listname, id=None):
    """search the title-name from a list with the id
    """

    if listname == "priority":
        mapped_title = map_priority(context, id)
    elif listname == "state":
        mapped_title = map_state(context, id)
    elif listname == "area":
        mapped_title = map_area(context, id)
    elif listname == "releases":
        mapped_title = map_release(context, id)
    else:
        mapped_title = ""

    return mapped_title


def map_priority(context, id=None):
    """search the title-name of a list with the id
    """
    if not id and getattr(context, 'getPriority', None):
        id = context.getPriority()

    priorities = context.getAvailablePriorities()
    for priority in priorities:
        if id == priority['id']:
            return priority['title']
    return "-"


# # HELPER Methods for ftw.table generator
def map_state(context, id=None):
    """search the title-name of a list with the id
    """

    if not id and getattr(context, 'getState', None):
        id = context.getState()
    states = context.getAvailableStates()
    for state in states:
        if id == state['id']:
            return state['title']
    return "-"


def map_area(context, id=None):
    """search the title-name of a list with the id
    """

    if not id and getattr(context, 'getArea', None):
        id = context.getArea()

    areas = context.getAvailableAreas()
    for area in areas:
        if id == area['id']:
            return area['title']
    return "-"


def map_release(context, id=None):
    """search the title-name of a list with the id
    """
    if not id and getattr(context, 'getReleases', None):
        id = context.getReleases()

    releases = context.getAvailableReleases()
    for release in releases:
        if id == release['id']:
            return release['title']
    return "-"


def readable_author(context):
    """
    get the full name of a user-id
    """
    author = context.responsibleManager
    if not author:
        return '-'
    name = author
    user = context.acl_users.getUserById(author)
    if user is None:
        return _(u"unassigned")
    else:
        name = user.getProperty('fullname', author)
        if not len(name):
            name = author
        return name
