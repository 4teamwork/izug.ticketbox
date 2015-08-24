from izug.ticketbox import ticketboxMessageFactory as _


def map_attribute(context, listname, id_=None):
    """search the title-name from a list with the id
    """

    if listname == "priority":
        mapped_title = map_priority(context, id_)

    elif listname == "state":
        mapped_title = map_state(context, id_)

    elif listname == "area":
        mapped_title = map_area(context, id_)

    elif listname == "variety":
        mapped_title = map_variety(context, id_)

    elif listname == "releases":
        mapped_title = map_release(context, id_)

    elif listname == "watchedRelease":
        mapped_title = map_watch_release(context, id_)

    else:
        mapped_title = ""

    return mapped_title


def map_priority(context, id_=None):
    """search the title-name of a list with the id
    """
    if not id_ and getattr(context, 'getPriority', None):
        id_ = context.getPriority()

    return map_base(context.getAvailablePriorities(), id_)


# # HELPER Methods for ftw.table generator
def map_state(context, id_=None):
    """search the title-name of a list with the id
    """

    if not id_ and getattr(context, 'getState', None):
        id_ = context.getState()
    return map_base(context.getAvailableStates(), id_)


def map_area(context, id_=None):
    """search the title-name of a list with the id
    """

    if not id_ and getattr(context, 'getArea', None):
        id_ = context.getArea()

    return map_base(context.getAvailableAreas(), id_)


def map_variety(context, id_=None):
    """search the title-name of a list with the id
    """
    if not id_ and getattr(context, 'getVariety', None):
        id_ = context.getVariety()

    return map_base(context.getAvailableVarieties(), id_)


def map_release(context, id_=None):
    """search the title-name of a list with the id
    """
    if not id_ and getattr(context, 'getReleases', None):
        id_ = context.getReleases()

    return map_base(context.getAvailableReleases(), id_)


def map_watch_release(context, id_=None):
    """search the title-name of a list with the id
    """
    if not id_ and getattr(context, 'getWatchedRelease', None):
        id_ = context.getWatchedRelease()

    return map_base(context.getAvailableReleases(), id_)


def map_base(available_items, id_):
    """Basemapping for attributes in ticketbox
    """
    for available_item in available_items:
        if id_ == available_item.get('id'):
            return available_item.get('title')
    return ""


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
