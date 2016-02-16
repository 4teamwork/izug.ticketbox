from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import functional_session_factory
from ftw.builder.testing import set_builder_session_factory
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.testing import z2
from zope.configuration import xmlconfig
import izug.ticketbox.tests.builder


class TicketBoxLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'
            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'

            '  <include package="Products.DataGridField" />'
            '</configure>',
            context=configurationContext)

        z2.installProduct(app, 'ftw.notification.base')
        z2.installProduct(app, 'ftw.notification.email')
        z2.installProduct(app, 'ftw.calendarwidget')
        z2.installProduct(app, 'izug.ticketbox')
        z2.installProduct(app, 'collective.MockMailHost')
        z2.installProduct(app, 'ftw.zipexport')

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, 'ftw.notification.base:default')
        applyProfile(portal, 'ftw.notification.email:default')
        applyProfile(portal, 'izug.ticketbox:default')
        applyProfile(portal, 'collective.MockMailHost:default')
        applyProfile(portal, 'ftw.zipexport:default')

TICKETBOX_FIXTURE = TicketBoxLayer()
TICKETBOX_INTEGRATION_TESTING = IntegrationTesting(
    bases=(TICKETBOX_FIXTURE, ), name="TicketBox:Integration")

TICKETBOX_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(TICKETBOX_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name="TicketBox:Functional")
