from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
from zope.interface import implements
from Acquisition import aq_parent


class TicketBoxVocabulary(object):
    """Vocabulary of all users which participates in this workspace.
    """

    implements(IVocabularyFactory)

    def __init__(self, field):
        self.field = field
        super(TicketBoxVocabulary, self).__init__

    def __call__(self, context, membersonly=False):
        tracker = aq_parent(context)
        myField = tracker.getField(self.field)
        for item in myField.get(tracker):
            yield SimpleVocabulary.createTerm(
            item['id'],item['id'],item['title'])


StatesVocabularyFactory=TicketBoxVocabulary('availableStates')
ReleasesVocabularyFactory=TicketBoxVocabulary('availableReleases')
SeveritiesVocabularyFactory=TicketBoxVocabulary('availableSeverities')
AreasVocabularyFactory=TicketBoxVocabulary('availableAreas')