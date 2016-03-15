# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from collective.contact.mailaction.testing import COLLECTIVE_CONTACT_MAILACTION_INTEGRATION_TESTING  # noqa
from plone import api

import unittest


class TestSetup(unittest.TestCase):
    """Test that collective.contact.mailaction is properly installed."""

    layer = COLLECTIVE_CONTACT_MAILACTION_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if collective.contact.mailaction is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'collective.contact.mailaction'))

    def test_browserlayer(self):
        """Test that ICollectiveContactMailactionLayer is registered."""
        from collective.contact.mailaction.interfaces import (
            ICollectiveContactMailactionLayer)
        from plone.browserlayer import utils
        self.assertIn(ICollectiveContactMailactionLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = COLLECTIVE_CONTACT_MAILACTION_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['collective.contact.mailaction'])

    def test_product_uninstalled(self):
        """Test if collective.contact.mailaction is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'collective.contact.mailaction'))
