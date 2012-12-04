from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.testing import z2
from zope.configuration import xmlconfig


class TicketBoxLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        import Products.DataGridField
        xmlconfig.file('configure.zcml', Products.DataGridField,
                       context=configurationContext)
        z2.installProduct(app, 'Products.DataGridField')

        import ftw.tabbedview
        xmlconfig.file('configure.zcml', ftw.tabbedview,
                       context=configurationContext)

        import izug.ticketbox
        xmlconfig.file('configure.zcml', izug.ticketbox,
                       context=configurationContext)
        z2.installProduct(app, 'izug.ticketbox')

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, 'izug.ticketbox:default')


TICKETBOX_FIXTURE = TicketBoxLayer()
TICKETBOX_INTEGRATION_TESTING = IntegrationTesting(
    bases=(TICKETBOX_FIXTURE, ), name="TicketBox:Integration")
TICKETBOX_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(TICKETBOX_FIXTURE, ), name="TicketBox:Functional")
