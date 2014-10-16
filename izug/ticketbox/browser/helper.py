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

    return map_base(context.getAvailableAreas(), id_, fallback_value='')


def map_variety(context, id_=None):
    """search the title-name of a list with the id
    """
    if not id_ and getattr(context, 'getVariety', None):
        id_ = context.getVariety()

    return map_base(context.getAvailableVarieties(), id_, fallback_value='')


def map_release(context, id_=None):
    """search the title-name of a list with the id
    """
    if not id_ and getattr(context, 'getReleases', None):
        id_ = context.getReleases()

    return map_base(context.getAvailableReleases(), id_, fallback_value='')


def map_watch_release(context, id_=None):
    """search the title-name of a list with the id
    """
    if not id_ and getattr(context, 'getWatchedRelease', None):
        id_ = context.getWatchedRelease()

    return map_base(context.getAvailableReleases(), id_, fallback_value='')


def map_base(available_items, id_, fallback_value='-'):
    """Basemapping for attributes in ticketbox
    """
    for available_item in available_items:
        if id_ == available_item.get('id'):
            return available_item.get('title')
    return fallback_value


def readable_user(user_id, context):
    """
    get the full name of a user-id
    """
    user = context.acl_users.getUserById(user_id)
    if user:
        return user.getProperty('fullname', user_id) or user_id
    return None


def readable_author(context):
    """
    get the full name of the author
    """
    author = context.getResponsibleManager()

    if not author:
        return '-'
    return readable_user(user_id=author, context=context) or _(u"unassigned")


def readable_issuer(context):
    """
    get the full name of the issuer
    """
    issuer = context.getIssuer()

    if not issuer:
        return '-'
    return readable_user(user_id=issuer, context=context) or _(u'No Issuer')