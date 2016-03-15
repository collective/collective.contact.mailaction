# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import collective.contact.mailaction


class CollectiveContactMailactionLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.loadZCML(package=collective.contact.mailaction)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.contact.mailaction:default')


COLLECTIVE_CONTACT_MAILACTION_FIXTURE = CollectiveContactMailactionLayer()


COLLECTIVE_CONTACT_MAILACTION_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_CONTACT_MAILACTION_FIXTURE,),
    name='CollectiveContactMailactionLayer:IntegrationTesting'
)


COLLECTIVE_CONTACT_MAILACTION_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_CONTACT_MAILACTION_FIXTURE,),
    name='CollectiveContactMailactionLayer:FunctionalTesting'
)


COLLECTIVE_CONTACT_MAILACTION_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        COLLECTIVE_CONTACT_MAILACTION_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='CollectiveContactMailactionLayer:AcceptanceTesting'
)
