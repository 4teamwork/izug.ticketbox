from ftw.builder.archetypes import ArchetypesBuilder
from ftw.builder import builder_registry


class TicketBoxBuilder(ArchetypesBuilder):
    portal_type = 'Ticket Box'

builder_registry.register('ticket box', TicketBoxBuilder)


class TicketBuilder(ArchetypesBuilder):
    portal_type = 'Ticket'

builder_registry.register('ticket', TicketBuilder)
