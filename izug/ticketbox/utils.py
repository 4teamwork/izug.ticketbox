from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import queryUtility


def uniquify_ids(data):
    """Creates unique ids within a list of dicts.
    Sets the "id" key of each dicts, creates the id with the value of
    "title" within the dict.

    ``data`` example:

    >>> [{'id': '', 'title': 'Foo'},
    ...  {'id': 'bar', 'title': 'Bar'}]
    """

    existing_ids = set([item.get('id') for item in data
                        if item.get('id')])

    for item in data:
        if item.get('id'):
            continue

        item['id'] = create_uniqe_id(item.get('title'), existing_ids)
        existing_ids.add(item['id'])

    return data


def create_uniqe_id(title, existing_ids):
    """Creates a uniqe id by using the IIDNormalizer utility.
    """

    id_ = queryUtility(IIDNormalizer).normalize(title)

    if id_ not in existing_ids:
        return id_

    base_id = id_
    index = 0

    while id_ in existing_ids:
        index += 1
        id_ = '%s-%i' % (base_id, index)

    return id_
