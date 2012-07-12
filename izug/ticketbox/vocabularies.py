from Acquisition import aq_parent
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary


class TicketBoxVocabulary(object):

    implements(IVocabularyFactory)

    def __init__(self, field):
        self.field = field

    def __call__(self, context):
        tracker = aq_parent(context)
        myField = tracker.getField(self.field)
        result = []
        for item in myField.get(tracker):
            result.append(SimpleVocabulary.createTerm(
                    item['id'], item['id'], item['title']))
        if result == []:
            result.append(SimpleVocabulary.createTerm(
                    '', '', '-'))
        return result


StatesVocabularyFactory = TicketBoxVocabulary('availableStates')
ReleasesVocabularyFactory = TicketBoxVocabulary('availableReleases')
PrioritiesVocabularyFactory = TicketBoxVocabulary('availablePriorities')
AreasVocabularyFactory = TicketBoxVocabulary('availableAreas')
VarietiesVocabularyFactory = TicketBoxVocabulary('availableVarieties')
