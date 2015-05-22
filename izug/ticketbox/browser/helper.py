from ftw.contenttemplates.interfaces import ICreateFromTemplate
from functools import partial
from izug.ticketbox import ticketboxMessageFactory as _
from plone import api
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter
from zope.component.hooks import getSite
import os


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


def get_fullname_by_user_id(user_id):
    """
    This method returns the full name of the given user id. En empty string
    is returned if the user is not found.
    """
    acl_users = getToolByName(getSite(), 'acl_users')
    user = acl_users.getUserById(user_id)
    if not user:
        return ''
    fullname = user.getProperty('fullname', user_id)
    if not fullname:
        return ''
    if isinstance(fullname, unicode):
        fullname = fullname.encode('utf-8')
    return fullname


def readable_author(context):
    """
    get the full name of the author
    """
    author = context.getResponsibleManager()

    if not author:
        return '-'
    return get_fullname_by_user_id(author) or _(u'unassigned')


def readable_issuer(context):
    """
    get the full name of the issuer
    """
    issuer = context.getIssuer()

    if not issuer or issuer == '(NOISSUER)':
        return '-'
    elif issuer == '(CREATOR)':
        return _(u'Creator')
    return get_fullname_by_user_id(issuer) or issuer


def get_template_factory_paths(obj):
    template_factory = getMultiAdapter((obj, obj.REQUEST), ICreateFromTemplate)
    template_factory_paths = template_factory.templatefolder_locations()

    # Prepend portal path to each template factory path
    prepend_portal_path = partial(os.path.join,
                                  *('/',) + api.portal.get().getPhysicalPath())
    template_factory_paths = map(prepend_portal_path, template_factory_paths)

    return template_factory_paths
