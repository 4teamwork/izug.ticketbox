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
    elif listname == "variety":
        mapped_title = map_variety(context, id)
    elif listname == "releases":
        mapped_title = map_release(context, id)
    elif listname == "watchedRelease":
         mapped_title = map_watch_release(context, id)
    else:
        mapped_title = ""

    return mapped_title


def map_priority(context, id=None):
    """search the title-name of a list with the id
    """
    if not id and getattr(context, 'getPriority', None):
        id = context.getPriority()

    return map_base(context.getAvailablePriorities(), id)


# # HELPER Methods for ftw.table generator
def map_state(context, id=None):
    """search the title-name of a list with the id
    """

    if not id and getattr(context, 'getState', None):
        id = context.getState()
    return map_base(context.getAvailableStates(), id)


def map_area(context, id=None):
    """search the title-name of a list with the id
    """

    if not id and getattr(context, 'getArea', None):
        id = context.getArea()

    return map_base(context.getAvailableAreas(), id)


def map_variety(context, id=None):
    """search the title-name of a list with the id
    """
    if not id and getattr(context, 'getVariety', None):
        id = context.getVariety()

    return map_base(context.getAvailableVarieties(), id)


def map_release(context, id=None):
    """search the title-name of a list with the id
    """
    if not id and getattr(context, 'getReleases', None):
        id = context.getReleases()

    return map_base(context.getAvailableReleases(), id)


def map_watch_release(context, id=None):
    """search the title-name of a list with the id
    """
    if not id and getattr(context, 'getWatchedRelease', None):
        id = context.getWatchedRelease()

    return map_base(context.getAvailableReleases(), id)


def map_base(available_items, id):
     """Basemapping for attributes in ticketbox
     """

     for available_item in available_items:
         if id == available_item.get('id'):
             return available_item.get('title')
     return "-"


def readable_author(context):
    """
    get the full name of a user-id
    """
    author = context.getResponsibleManager()

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
