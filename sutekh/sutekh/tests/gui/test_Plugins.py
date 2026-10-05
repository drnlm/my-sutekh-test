# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Copyright 2021 Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - see COPYING for details
# Partly inspired by https://gist.github.com/brantfaircloth/764363

"""Test that plugins can be imported / support the correct versions"""

# This is not a functional test of any of the plugins as plugins can
# provide their own test classes for that, but aims to catch plugins
# that have not been updated to changes to the database schema and
# so forth. This is a simple 'counting fingers' sanity test

import unittest

from sutekh.tests.GuiSutekhTest import ConfigSutekhTest


from sutekh.base.gui.BasePluginManager import submodules
from sutekh.gui.PluginManager import PluginManager
import sutekh.gui.plugins as plugins


aCandPlugins = sorted(submodules(plugins))
aFailed = []
aImported = []

# pylint: disable=invalid-name
# We use mPlugin to match the implementation

class TestPluginVersionImport(ConfigSutekhTest):
    """Class for testing version support for plugins.

       This is not a GuiSutekhTest, as we don't need all the plumbing"""

    def test_imports(self):
        """Test that included plugins are importable and support the current
           table versions"""
        aFailedVersions = []
        aSeenPlugins = set()
        aSeenTests = set()
        aDuplicatePluginClasses = []
        aDuplicatePluginTests = []

        for sPluginName in aCandPlugins:
            try:
                mPlugin = __import__("%s.%s" % (PluginManager.sPluginDir,
                                                sPluginName), None, None,
                                                [plugins])
                if not hasattr(mPlugin, 'plugin'):
                    continue
                cPlugin = mPlugin.plugin
                if not issubclass(cPlugin, PluginManager.cAppPlugin):
                    continue
                aImported.append((mPlugin, sPluginName))
            except Exception as err:
                aFailed.append((sPluginName, err))
                continue

        for mPlugin, sPluginName in aImported:
            if not cPlugin.check_versions():
                aFailedVersion.append(sPluginName)
            if mPlugin.plugin.__name__ in aSeenPlugins:
                aDuplicatePluginClasses.append(mPlugin.plugin.__name__)
            aSeenPlugins.add(mPlugin.plugin.__name__)
        self.assertEqual(aFailed, [], "Failed import check")
        self.assertEqual(aFailedVersions, [], "Failed version check")
        self.assertEqual(aDuplicatePluginClasses, [], "Duplicate plugin class names seen")
        self.assertEqual(aDuplicatePluginTests, [], "Duplicate plugin test class names seen")
